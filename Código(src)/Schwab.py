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

# Obtiene tickers únicos desde la base de datos, sin filtrar por fecha
def obtener_tickers_unicos():
    conn = conectar()
    if conn:
        try:
            query_filtro = None  # Sin filtro de fecha
            datos = leer_datos(conn, "TablaFinviz", query_filtro)
            tickers = list(set(row[1] for row in datos)) if datos else []  # Tickers únicos
            print(f"[DEBUG] Tickers únicos obtenidos: {len(tickers)}")
            return tickers
        except Exception as e:
            print(f"[DEBUG] Error al leer tickers: {e}")
        finally:
            conn.close()
    return []

# Obtiene volúmenes para una lista de tickers usando la API de Schwab
async def obtener_volumenes_schwab(tickers):
    try:
        # Autenticación
        client = easy_client(API_KEY, APP_SECRET, CALLBACK_URI, TOKEN_PATH)
        batch_size = 100  # Tickers por solicitud
        volumenes = {}
        today = datetime.now().strftime('%Y-%m-%d')

        # Procesar tickers en lotes
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
                                volume = quote_data[ticker]['quote'].get('totalVolume', 0)
                                volumenes[ticker] = volume if volume > 0 else None
                                print(f"[DEBUG] {ticker}: {volume} acciones")
                            else:
                                volumenes[ticker] = None
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
                            volumenes[ticker] = None
                        break
                    time.sleep(2 ** (3 - retries))  # Espera exponencial
            time.sleep(0.5)  # Evitar límite de tasa
        return volumenes
    except Exception as e:
        print(f"[DEBUG] Error al obtener volúmenes: {e}")
        traceback.print_exc()
        return {}

# Actualiza o inserta el volumen de un ticker en la base de datos
def actualizar_volumen_actual(ticker, volumen_actual, fecha):
    conn = conectar()
    if conn:
        cursor = conn.cursor()
        try:
            fecha_str = fecha.strftime("%Y-%m-%d")
            # Verifica si existe un registro para el ticker y la fecha
            query_check = """
            SELECT COUNT(*) FROM [TablaFinviz]
            WHERE [Ticker] = ? AND [Fecha] = ?
            """
            cursor.execute(query_check, (ticker, fecha_str))
            exists = cursor.fetchone()[0] > 0

            if exists:
                # Actualiza el registro existente
                query_update = """
                UPDATE [TablaFinviz]
                SET [VolumenActual] = ?
                WHERE [Ticker] = ? AND [Fecha] = ?
                """
                valores = (volumen_actual if volumen_actual is not None else None, ticker, fecha_str)
                cursor.execute(query_update, valores)
                print(f"[DEBUG] Volumen actualizado para {ticker} en {fecha_str}: {volumen_actual}")
            else:
                # Inserta un nuevo registro
                query_insert = """
                INSERT INTO [TablaFinviz] ([Ticker], [Fecha], [VolumenActual])
                VALUES (?, ?, ?)
                """
                valores = (ticker, fecha_str, volumen_actual if volumen_actual is not None else None)
                cursor.execute(query_insert, valores)
                print(f"[DEBUG] Volumen insertado para {ticker} en {fecha_str}: {volumen_actual}")

            conn.commit()
        except Exception as e:
            print(f"[DEBUG] Error al actualizar/insertar volumen para {ticker}: {e}")
        finally:
            cursor.close()
            conn.close()

# Opción 2: Actualizar todos los registros de un ticker, sin importar la fecha
"""
def actualizar_volumen_actual(ticker, volumen_actual):
    conn = conectar()
    if conn:
        cursor = conn.cursor()
        try:
            query = '''
            UPDATE [TablaFinviz]
            SET [VolumenActual] = ?
            WHERE [Ticker] = ?
            '''
            valores = (volumen_actual if volumen_actual is not None else None, ticker)
            cursor.execute(query, valores)
            conn.commit()
            print(f"[DEBUG] Volumen actualizado para {ticker}: {volumen_actual}")
        except Exception as e:
            print(f"[DEBUG] Error al actualizar volumen para {ticker}: {e}")
        finally:
            cursor.close()
            conn.close()
"""

# Función principal
async def main():
    print(f"[scraper_schwab] Iniciando actualización de volumen a las {datetime.now().strftime('%H:%M:%S')}...")
    fecha_actual = obtener_fecha_actual()
    tickers = obtener_tickers_unicos()
    
    if not tickers:
        print(f"[scraper_schwab] No se encontraron tickers en TablaFinviz.")
        return

    print(f"[scraper_schwab] Obteniendo volúmenes para {len(tickers)} tickers únicos...")
    volumenes = await obtener_volumenes_schwab(tickers)

    print(f"[scraper_schwab] Actualizando volúmenes en la base de datos...")
    for ticker in tickers:
        volumen_actual = volumenes.get(ticker)
        if volumen_actual is not None:
            actualizar_volumen_actual(ticker, volumen_actual, fecha_actual)
            # Para Opción 2, usa:
            # actualizar_volumen_actual(ticker, volumen_actual)
        else:
            print(f"[DEBUG] Sin volumen para {ticker}, no se actualiza.")

    print("[scraper_schwab] Actualización de volúmenes completada.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"[DEBUG] Error al ejecutar el script: {e}")
        traceback.print_exc()