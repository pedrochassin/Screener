import yfinance as yf
from Base_Datos import conectar, leer_datos
import time
from datetime import datetime, timedelta, date
from pytz import timezone
from utils import obtener_fecha_actual

# Obtiene la hora actual en la zona horaria del este de EE.UU.
def obtener_hora_actual():
    return datetime.now(timezone("US/Eastern"))

# Obtiene los tickers y sus fechas desde la base de datos, filtrados por un rango de 3 días atrás hasta hoy
def obtener_tickers_y_fechas():
    conn = conectar()
    if conn:
        try:
            fecha_actual = obtener_fecha_actual()
            fecha_inicio = (fecha_actual - timedelta(days=3)).strftime("%Y-%m-%d")
            fecha_actual_str = fecha_actual.strftime("%Y-%m-%d")
            query_filtro = f"Fecha BETWEEN '{fecha_inicio}' AND '{fecha_actual_str}'"
            datos = leer_datos(conn, "TablaFinviz", query_filtro)
            tickers_fechas = [(row[1], row[0]) for row in datos] if datos else []
            print(f"[DEBUG] Tickers y fechas obtenidos: {len(tickers_fechas)} registros entre {fecha_inicio} y {fecha_actual_str}")
            return tickers_fechas
        except Exception as e:
            print(f"[DEBUG] Error al leer tickers y fechas: {e}")
        finally:
            conn.close()
    return []

# Obtiene el volumen para una fecha específica para un ticker
def scrapear_volumen_actual(ticker, fecha):
    try:
        stock = yf.Ticker(ticker)
        if isinstance(fecha, str):
            fecha = datetime.strptime(fecha, "%Y-%m-%d")
        hist = stock.history(start=fecha, end=fecha + timedelta(days=1))
        print(f"[DEBUG] Datos para {ticker} en {fecha}: {hist}")
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
        hist = stock.history(start=fecha, end=fecha + timedelta(days=1))
        if hist.empty:
            print(f"[DEBUG] No datos históricos para {ticker} en {fecha}")
            return None
        datos = {
            "Open": float(hist["Open"].iloc[0]),
            "Close": float(hist["Close"].iloc[0]),
            "High": float(hist["High"].iloc[0]),
            "Low": float(hist["Low"].iloc[0])
        }
        print(f"[DEBUG] Datos históricos para {ticker}: {datos}")
        return datos
    except Exception as e:
        print(f"[DEBUG] Error al scrapear datos históricos para {ticker}: {e}")
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
            fecha_str = fecha.strftime("%Y-%m-%d") if isinstance(fecha, (datetime, date)) else fecha
            valores = (
                datos_historicos["Open"],
                datos_historicos["Close"],
                datos_historicos["High"],
                datos_historicos["Low"],
                ticker,
                fecha_str
            )
            cursor.execute(query, valores)
            conn.commit()
            print(f"[DEBUG] Datos históricos actualizados para {ticker} en {fecha_str}")
        except Exception as e:
            print(f"[DEBUG] Error al actualizar datos históricos para {ticker}: {e}")
        finally:
            cursor.close()
            conn.close()

# Actualiza el volumen de un ticker en la base de datos para una fecha específica
def actualizar_volumen_actual(ticker, volumen_actual, fecha):
    conn = conectar()
    if conn:
        cursor = conn.cursor()
        try:
            query = """
            UPDATE [TablaFinviz]
            SET [VolumenActual] = ?
            WHERE [Ticker] = ? AND [Fecha] = ?
            """
            fecha_str = fecha.strftime("%Y-%m-%d") if isinstance(fecha, (datetime, date)) else fecha
            valores = (volumen_actual if volumen_actual is not None else None, ticker, fecha_str)
            cursor.execute(query, valores)
            conn.commit()
            print(f"[DEBUG] Volumen actualizado para {ticker} en {fecha_str}: {volumen_actual}")
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
    print(f"[scraper_yahoo] Iniciando actualización a las {datetime.now().strftime('%H:%M:%S')}...")
    tickers_fechas = obtener_tickers_y_fechas()
    if not tickers_fechas:
        fecha_actual = obtener_fecha_actual()
        fecha_inicio = (fecha_actual - timedelta(days=3)).strftime("%Y-%m-%d")
        fecha_actual_str = fecha_actual.strftime("%Y-%m-%d")
        print(f"[scraper_yahoo] No se encontraron tickers entre {fecha_inicio} y {fecha_actual_str} en TablaFinviz.")
        return

    print("[scraper_yahoo] Iniciando actualización de datos históricos...")
    for ticker, fecha in tickers_fechas:
        datos_historicos = scrapear_datos_historicos(ticker, fecha)
        if datos_historicos:
            actualizar_datos_historicos(ticker, datos_historicos, fecha)

    print("[scraper_yahoo] Iniciando actualización de VolumenActual para los últimos 3 días...")
    for ticker, fecha in tickers_fechas:
        volumen_actual = scrapear_volumen_actual(ticker, fecha)
        if volumen_actual is not None:
            actualizar_volumen_actual(ticker, volumen_actual, fecha)

    print("[scraper_yahoo] Ejecutando procedimiento almacenado...")
    ejecutar_procedimiento()

    print("[scraper_yahoo] Actualización completada.")

if __name__ == "__main__":
    main()