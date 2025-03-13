import yfinance as yf
from Base_Datos import conectar, leer_datos
import time
from datetime import datetime
from pytz import timezone
from datetime import datetime

def obtener_hora_actual():
    return datetime.now(timezone("US/Eastern"))  # Horario de Nueva York


def obtener_tickers_y_fechas():
    """Obtiene todos los tickers y fechas de TablaFinviz."""
    conn = conectar()
    if conn:
        try:
            datos = leer_datos(conn, "TablaFinviz")
            tickers_fechas = [(row[1], row[0]) for row in datos]  # Ticker (índice 1), Fecha (índice 0)
            return tickers_fechas
        except Exception as e:
            print(f"Error al leer tickers y fechas: {e}")
        finally:
            conn.close()
    return []

def scrapear_volumen_actual(ticker):
    """Scrapea el volumen actual (último minuto) del día actual."""
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1d", interval="1d")
        print(f"Datos recibidos para {ticker}:\n{hist.tail(5)}")  # 🔎 Verifica los últimos 5 registros
        if hist.empty:
            print(f"No se encontraron datos intradiarios para {ticker}")
            return None
        
        # Asegúrate de que 'Volume' no esté vacío ni sea NaN
        if 'Volume' in hist.columns and not hist['Volume'].isnull().all():
            volumen = int(hist['Volume'].dropna().iloc[-1])
            return volumen
        else:
            print(f"Volumen vacío para {ticker}")
            return 0
    except Exception as e:
        print(f"Error al scrapear volumen actual para {ticker}: {e}")
        return None


def scrapear_datos_historicos(ticker, fecha):
    """Scrapea Open, Close, High, Low para una fecha específica."""
    try:
        stock = yf.Ticker(ticker)
        if isinstance(fecha, str):
            fecha = datetime.strptime(fecha, "%Y-%m-%d")
        hist = stock.history(start=fecha, end=fecha + timedelta(days=1))
        if hist.empty:
            print(f"No se encontraron datos históricos para {ticker} en {fecha}")
            return None
        datos = {
            "Open": float(hist["Open"].iloc[0]),
            "Close": float(hist["Close"].iloc[0]),
            "High": float(hist["High"].iloc[0]),
            "Low": float(hist["Low"].iloc[0])
        }
        return datos
    except Exception as e:
        print(f"Error al scrapear datos históricos para {ticker}: {e}")
        return None

def actualizar_datos_historicos(ticker, datos_historicos):
    """Actualiza los datos históricos solo una vez."""
    conn = conectar()
    if conn:
        try:
            cursor = conn.cursor()
            query = """
            UPDATE [TablaFinviz]
            SET [Open] = ?,
                [Close] = ?,
                [High] = ?,
                [Low] = ?
            WHERE [Ticker] = ?
            """
            valores = (
                datos_historicos["Open"],
                datos_historicos["Close"],
                datos_historicos["High"],
                datos_historicos["Low"],
                ticker
            )
            cursor.execute(query, valores)
            conn.commit()
            print(f"Datos históricos actualizados para {ticker}")
        except Exception as e:
            print(f"Error al actualizar datos históricos para {ticker}: {e}")
        finally:
            cursor.close()
            conn.close()

def actualizar_volumen_actual(ticker, volumen_actual):
    """Actualiza solo VolumenActual en cada iteración."""
    conn = conectar()
    if conn:
        try:
            cursor = conn.cursor()
            query = """
            UPDATE [TablaFinviz]
            SET [VolumenActual] = ?
            WHERE [Ticker] = ?
            """
            valores = (volumen_actual, ticker)
            cursor.execute(query, valores)
            conn.commit()
            print(f"Volumen actual actualizado para {ticker}: {volumen_actual}")
        except Exception as e:
            print(f"Error al actualizar volumen para {ticker}: {e}")
        finally:
            cursor.close()
            conn.close()

def main():
    """Scrapea datos históricos una vez y actualiza VolumenActual cada minuto."""
    tickers_fechas = obtener_tickers_y_fechas()
    if not tickers_fechas:
        print("No se encontraron tickers en TablaFinviz.")
        return
    
    # Actualización inicial de datos históricos
    print("Realizando actualización inicial de datos históricos...")
    for ticker, fecha in tickers_fechas:
        datos_historicos = scrapear_datos_historicos(ticker, fecha)
        if datos_historicos:
            actualizar_datos_historicos(ticker, datos_historicos)
    
    # Bucle para actualizar solo VolumenActual cada minuto
    print("Iniciando actualización continua de VolumenActual...")
    while True:
        print(f"Actualizando VolumenActual a las {datetime.now()}")
        for ticker, _ in tickers_fechas:  # Ignoramos fecha aquí
            volumen_actual = scrapear_volumen_actual(ticker)
            if volumen_actual is not None:
                actualizar_volumen_actual(ticker, volumen_actual)
        
        print("Esperando 1 hora para la próxima actualización...")
        time.sleep(3600)  # Espera 1 hora antes de la próxima actualización

if __name__ == "__main__":
    from datetime import timedelta
    main()