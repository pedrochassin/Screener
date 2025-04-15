import sys
import traceback
from datetime import datetime
import asyncio
import time
from itertools import islice
from Base_Datos import conectar, leer_datos
from utils import obtener_fecha_actual

print(f"Python version: {sys.version}")
try:
    from schwab.auth import easy_client
    from schwab.client import Client
except ImportError as e:
    print(f"[DEBUG] Error al importar módulos de schwab-py: {e}")
    traceback.print_exc()
    print("[DEBUG] Intenta: pip install schwab-py")
    sys.exit(1)

# Configura tus credenciales de Schwab
API_KEY = 'ehTixVSLNfKsmi37c31YJVEAA8fMZ54G'  # Reemplaza con tu clave API
APP_SECRET = 'TGW90ZhxR9zHUcve'  # Reemplaza con tu secreto API
CALLBACK_URI = 'https://127.0.0.1'  # Ajusta según el portal
TOKEN_PATH = 'token.json'  # Archivo para almacenar el token

# Número de tickers para pruebas
TICKERS_LIMIT = 10  # Cambia a None para todos los tickers

# Obtiene tickers únicos desde la base de datos
def obtener_tickers_unicos(limit=None):
    conn = conectar()
    if conn:
        try:
            query_filtro = None
            datos = leer_datos(conn, "TablaFinviz", query_filtro)
            tickers = list(set(row[1] for row in datos)) if datos else []
            if limit is not None:
                tickers = tickers[:limit]
            print(f"[DEBUG] Tickers únicos obtenidos: {len(tickers)}")
            return tickers
        except Exception as e:
            print(f"[DEBUG] Error al leer tickers: {e}")
        finally:
            conn.close()
    return []

# Obtiene datos actuales de Schwab
async def obtener_datos_schwab(tickers):
    try:
        client = easy_client(API_KEY, APP_SECRET, CALLBACK_URI, TOKEN_PATH)
        batch_size = 100
        datos = {}
        today = datetime.now().strftime('%Y-%m-%d')

        for i in range(0, len(tickers), batch_size):
            batch = tickers[i:i + batch_size]
            retries = 3
            while retries > 0:
                try:
                    print(f"[DEBUG] Procesando lote {i//batch_size + 1}/{len(tickers)//batch_size + 1}...")
                    quote_response = client.get_quotes(symbols=batch)

                    if quote_response.status_code == 200:
                        quote_data = quote_response.json()
                        for ticker in batch:
                            if ticker in quote_data and 'quote' in quote_data[ticker]:
                                quote = quote_data[ticker]['quote']
                                fundamental = quote_data[ticker].get('fundamental', {})
                                high = quote.get('highPrice', 0)
                                low = quote.get('lowPrice', 0)
                                ret = ((high - low) / low * 100) if low > 0 else 0
                                volume = quote.get('totalVolume', 0)
                                avg_vol = fundamental.get('avg10DaysVolume', 0)
                                rvo = volume / avg_vol if avg_vol > 0 else 0
                                # Genera barra de estado para Rvo (usando asteriscos para compatibilidad)
                                rvo_normalized = min(max(rvo, 0), 5)
                                rvo_bar = '*' * int(rvo_normalized * 2)
                                rvo_bar = rvo_bar.ljust(10)
                                
                                datos[ticker] = {
                                    'Price': quote.get('lastPrice', 0),
                                    'Change%': quote.get('netPercentChange', 0),
                                    'Volume': volume,
                                    'AvgVol': avg_vol,
                                    'Rvo': rvo,
                                    'Ret': ret,
                                    'RvoBar': rvo_bar
                                }
                                print(f"[DEBUG] {ticker}: Price={datos[ticker]['Price']}, Change%={datos[ticker]['Change%']:.2f}, Volume={volume}, AvgVol={avg_vol:.0f}, Rvo={rvo:.2f}, Ret={ret:.2f}, RvoBar={rvo_bar}")
                            else:
                                datos[ticker] = {'Price': 0, 'Change%': 0, 'Volume': 0, 'AvgVol': 0, 'Rvo': 0, 'Ret': 0, 'RvoBar': ''}
                                print(f"[DEBUG] No se encontraron datos para {ticker}")
                        break
                    else:
                        print(f"[DEBUG] Error en get_quotes: {quote_response.status_code}")
                        print(f"[DEBUG] Detalles: {quote_response.text}")
                        raise Exception("Fallo en la solicitud")
                except Exception as e:
                    retries -= 1
                    print(f"[DEBUG] Error: {e}. Reintentos restantes: {retries}")
                    if retries == 0:
                        print(f"[DEBUG] Fallo en lote {batch}. Saltando...")
                        for ticker in batch:
                            datos[ticker] = {'Price': 0, 'Change%': 0, 'Volume': 0, 'AvgVol': 0, 'Rvo': 0, 'Ret': 0, 'RvoBar': ''}
                        break
                    time.sleep(2 ** (3 - retries))
            time.sleep(0.5)
        return datos
    except Exception as e:
        print(f"[DEBUG] Error al obtener datos de Schwab: {e}")
        traceback.print_exc()
        return {}

# Crea o actualiza la tabla TempDatosActuales y guarda datos
def guardar_datos_actuales(datos):
    conn = conectar()
    if conn:
        cursor = conn.cursor()
        try:
            # Crea tabla si no existe
            cursor.execute("""
            IF OBJECT_ID('TempDatosActuales') IS NULL
                CREATE TABLE TempDatosActuales (
                    Ticker VARCHAR(50),
                    Price FLOAT,
                    ChangePercent FLOAT,
                    Volume BIGINT,
                    AvgVol FLOAT,
                    Rvo FLOAT,
                    Ret FLOAT,
                    RvoBar VARCHAR(10)
                );
            """)
            # Trunca la tabla
            cursor.execute("TRUNCATE TABLE TempDatosActuales;")

            # Inserta datos
            for ticker, info in datos.items():
                query = """
                INSERT INTO TempDatosActuales (Ticker, Price, ChangePercent, Volume, AvgVol, Rvo, Ret, RvoBar)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """
                valores = (
                    ticker,
                    info['Price'],
                    info['Change%'],
                    info['Volume'],
                    info['AvgVol'],
                    info['Rvo'],
                    info['Ret'],
                    info['RvoBar']
                )
                cursor.execute(query, valores)
                print(f"[DEBUG] Datos insertados para {ticker}")

            conn.commit()
        except Exception as e:
            print(f"[DEBUG] Error al guardar datos: {e}")
        finally:
            cursor.close()
            conn.close()

# Crea la vista DatosActuales con formato personalizado
def crear_vista_datos_actuales():
    conn = conectar()
    if conn:
        cursor = conn.cursor()
        try:
            # Ejecuta DROP VIEW por separado
            cursor.execute("""
            IF OBJECT_ID('DatosActuales') IS NOT NULL
                DROP VIEW DatosActuales;
            """)
            conn.commit()

            # Crea la vista con formato
            cursor.execute("""
            CREATE VIEW DatosActuales AS
            SELECT 
                Ticker,
                CAST(Price AS DECIMAL(10,2)) AS Price,
                FORMAT(ChangePercent, 'N2') + '%' AS [Change%],
                FORMAT(Volume, 'N0') AS Volume,
                FORMAT(AvgVol, 'N0') AS AvgVol,
                CAST(Rvo AS DECIMAL(10,2)) AS Rvo,
                CAST(Ret AS DECIMAL(10,2)) AS Ret,
                RvoBar
            FROM TempDatosActuales;
            """)
            conn.commit()
            print(f"[DEBUG] Vista DatosActuales creada con éxito.")
        except Exception as e:
            print(f"[DEBUG] Error al crear vista: {e}")
        finally:
            cursor.close()
            conn.close()

# Función principal
async def main():
    print(f"[scraper_schwab] Iniciando generación de datos actuales a las {datetime.now().strftime('%H:%M:%S')}...")
    tickers = obtener_tickers_unicos(limit=TICKERS_LIMIT)
    
    if not tickers:
        print(f"[scraper_schwab] No se encontraron tickers en TablaFinviz.")
        return

    print(f"[scraper_schwab] Obteniendo datos para {len(tickers)} tickers únicos...")
    datos = await obtener_datos_schwab(tickers)

    print(f"[scraper_schwab] Guardando datos en tabla TempDatosActuales...")
    guardar_datos_actuales(datos)

    print(f"[scraper_schwab] Creando vista DatosActuales...")
    crear_vista_datos_actuales()

    print("[scraper_schwab] Generación de datos completada.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"[DEBUG] Error al ejecutar el script: {e}")
        traceback.print_exc()