import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import yfinance as yf
from Base_Datos import conectar, leer_datos  # Ahora funciona desde archivo/
import time
from datetime import datetime, timedelta
from pytz import timezone

# Obtiene la hora actual en la zona horaria del este de EE.UU.
def obtener_hora_actual():
    return datetime.now(timezone("US/Eastern"))

# Obtiene los tickers y sus fechas desde la base de datos
def obtener_tickers_y_fechas():
    conn = conectar()
    if conn:
        try:
            datos = leer_datos(conn, "TablaFinviz")
            tickers_fechas = [(row[1], row[0]) for row in datos]
            print(f"[DEBUG] Tickers y fechas obtenidos: {len(tickers_fechas)} registros")
            return tickers_fechas
        except Exception as e:
            print(f"[DEBUG] Error al leer tickers y fechas: {e}")
        finally:
            conn.close()
    return []

# Obtiene el volumen de un ticker para una fecha específica
def scrapear_volumen_fecha(ticker, fecha):
    try:
        stock = yf.Ticker(ticker)
        if isinstance(fecha, str):
            fecha = datetime.strptime(fecha, "%Y-%m-%d")
        hist = stock.history(start=fecha, end=fecha + timedelta(days=1), interval="1d")
        print(f"[DEBUG] Datos para {ticker} en {fecha}: {hist.tail(1)}")
        if hist.empty:
            print(f"[DEBUG] No se encontraron datos para {ticker} en {fecha}")
            return None
        if 'Volume' in hist.columns and not hist['Volume'].isnull().all():
            volumen = int(hist['Volume'].dropna().iloc[-1])
            return volumen if volumen > 0 else None
        else:
            print(f"[DEBUG] Volumen vacío para {ticker} en {fecha}")
            return None
    except Exception as e:
        print(f"[DEBUG] Error al scrapear volumen para {ticker} en {fecha}: {e}")
        return None

# Obtiene los datos históricos de un ticker en una fecha específica
def scrapear_datos_historicos(ticker, fecha):
    try:
        stock = yf.Ticker(ticker)
        if isinstance(fecha, str):
            fecha = datetime.strptime(fecha, "%Y-%m-%d")
        hist = stock.history(start=fecha, end=fecha + timedelta(days=1), interval="1d")
        if hist.empty:
            print(f"[DEBUG] No datos históricos para {ticker} en {fecha}")
            return None
        datos = {
            "Open": float(hist["Open"].iloc[0]),
            "Close": float(hist["Close"].iloc[0]),
            "High": float(hist["High"].iloc[0]),
            "Low": float(hist["Low"].iloc[0])
        }
        print(f"[DEBUG] Datos históricos para {ticker} en {fecha}: {datos}")
        return datos
    except Exception as e:
        print(f"[DEBUG] Error al scrapear datos históricos para {ticker} en {fecha}: {e}")
        return None

# Actualiza los datos históricos de un ticker en la base de datos
def actualizar_datos_historicos(ticker, datos_historicos, fecha):
    conn = conectar()
    if conn:
        cursor = conn.cursor()
        try:
            query = """
            UPDATE [TablaFinviz]
            SET [Open] = ?,
                [Close] = ?,
                [High] = ?,
                [Low] = ?
            WHERE [Ticker] = ? AND [Fecha] = ?
            """
            valores = (
                datos_historicos["Open"],
                datos_historicos["Close"],
                datos_historicos["High"],
                datos_historicos["Low"],
                ticker,
                fecha.strftime("%Y-%m-%d") if isinstance(fecha, datetime) else fecha
            )
            cursor.execute(query, valores)
            conn.commit()
            print(f"[DEBUG] Datos históricos actualizados para {ticker} en {fecha}")
        except Exception as e:
            print(f"[DEBUG] Error al actualizar datos históricos para {ticker}: {e}")
        finally:
            cursor.close()
            conn.close()

# Actualiza el volumen de un ticker en la base de datos para una fecha específica
def actualizar_volumen_fecha(ticker, volumen, fecha):
    conn = conectar()
    if conn:
        cursor = conn.cursor()
        try:
            query = """
            UPDATE [TablaFinviz]
            SET [VolumenActual] = ?
            WHERE [Ticker] = ? AND [Fecha] = ?
            """
            valores = (
                volumen if volumen is not None else None,
                ticker,
                fecha.strftime("%Y-%m-%d") if isinstance(fecha, datetime) else fecha
            )
            cursor.execute(query, valores)
            conn.commit()
            print(f"[DEBUG] Volumen actualizado para {ticker} en {fecha}: {volumen}")
        except Exception as e:
            print(f"[DEBUG] Error al actualizar volumen para {ticker}: {e}")
        finally:
            cursor.close()
            conn.close()

# Ejecuta el procedimiento almacenado que calcula Rvol y Return
def ejecutar_procedimiento():
    conn = conectar()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("EXEC CalcularRvolYReturn;")
            conn.commit()
            print(f"[DEBUG] Procedimiento almacenado ejecutado con éxito.")
        except Exception as e:
            print(f"[DEBUG] Error al ejecutar el procedimiento almacenado: {e}")
        finally:
            cursor.close()
            conn.close()

# Función principal que gestiona el flujo de actualización de datos
def main():
    tickers_fechas = obtener_tickers_y_fechas()
    if not tickers_fechas:
        print("[DEBUG] No se encontraron tickers en TablaFinviz.")
        return

    print("[DEBUG] Iniciando actualización de datos históricos...")
    for ticker, fecha in tickers_fechas:
        datos_historicos = scrapear_datos_historicos(ticker, fecha)
        if datos_historicos:
            actualizar_datos_historicos(ticker, datos_historicos, fecha)

    print("[DEBUG] Iniciando actualización de VolumenActual...")
    for ticker, fecha in tickers_fechas:
        volumen = scrapear_volumen_fecha(ticker, fecha)
        if volumen is not None:
            actualizar_volumen_fecha(ticker, volumen, fecha)

    print("[DEBUG] Ejecutando procedimiento almacenado...")
    ejecutar_procedimiento()

if __name__ == "__main__":
    main()