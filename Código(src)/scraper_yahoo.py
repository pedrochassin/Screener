import yfinance as yf
from Base_Datos import conectar, leer_datos
import time
import threading
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

# Obtiene el volumen acumulado del día actual para un ticker
def scrapear_volumen_actual(ticker):
    try:
        stock = yf.Ticker(ticker)
        # Usa period="1d" para obtener el volumen acumulado del día actual
        hist = stock.history(period="1d", interval="1d")
        print(f"[DEBUG] Datos diarios para {ticker}: {hist.tail(1)}")
        if hist.empty:
            print(f"[DEBUG] No se encontraron datos para {ticker}")
            return None
        if 'Volume' in hist.columns and not hist['Volume'].isnull().all():
            volumen = int(hist['Volume'].dropna().iloc[-1])
            return volumen if volumen > 0 else None
        else:
            print(f"[DEBUG] Volumen vacío para {ticker}")
            return None
    except Exception as e:
        print(f"[DEBUG] Error al scrapear volumen para {ticker}: {e}")
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
def actualizar_datos_historicos(ticker, datos_historicos):
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
            print(f"[DEBUG] Datos históricos actualizados para {ticker}")
        except Exception as e:
            print(f"[DEBUG] Error al actualizar datos históricos para {ticker}: {e}")
        finally:
            cursor.close()
            conn.close()

# Actualiza el volumen actual de un ticker en la base de datos
def actualizar_volumen_actual(ticker, volumen_actual):
    conn = conectar()
    if conn:
        try:
            cursor = conn.cursor()
            query = """
            UPDATE [TablaFinviz]
            SET [VolumenActual] = ?
            WHERE [Ticker] = ?
            """
            valores = (volumen_actual if volumen_actual is not None else None, ticker)
            cursor.execute(query, valores)
            conn.commit()
            print(f"[DEBUG] Volumen actualizado para {ticker}: {volumen_actual}")
        except Exception as e:
            print(f"[DEBUG] Error al actualizar volumen para {ticker}: {e}")
        finally:
            cursor.close()
            conn.close()

# Ejecuta el procedimiento almacenado que calcula Rvol y Return
def ejecutar_procedimiento():
    conn = conectar()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("EXEC CalcularRvolYReturn;")
            conn.commit()
            print(f"[DEBUG] Procedimiento almacenado ejecutado con éxito.")
        except Exception as e:
            print(f"[DEBUG] Error al ejecutar el procedimiento almacenado: {e}")
        finally:
            cursor.close()
            conn.close()

# Función para manejar la actualización periódica del VolumenActual
def actualizar_volumen_continuo(intervalo_segundos=3600):
    while True:  # Bucle infinito para actualizaciones continuas
        tickers_fechas = obtener_tickers_y_fechas()
        if not tickers_fechas:
            print("[DEBUG] No se encontraron tickers para actualizar VolumenActual.")
            time.sleep(intervalo_segundos)
            continue

        print(f"[DEBUG] Actualizando VolumenActual a las {datetime.now()}")
        for ticker, _ in tickers_fechas:
            volumen_actual = scrapear_volumen_actual(ticker)
            if volumen_actual is not None:
                actualizar_volumen_actual(ticker, volumen_actual)
        ejecutar_procedimiento()

        print(f"[DEBUG] Esperando {intervalo_segundos // 60} minutos para la próxima actualización...")
        time.sleep(intervalo_segundos)

# Función principal que gestiona el flujo de actualización de datos
def main():
    tickers_fechas = obtener_tickers_y_fechas()
    if not tickers_fechas:
        print("[DEBUG] No se encontraron tickers en TablaFinviz.")
        return

    print("[DEBUG] Iniciando actualización inicial de datos históricos...")
    for ticker, fecha in tickers_fechas:
        datos_historicos = scrapear_datos_historicos(ticker, fecha)
        if datos_historicos:
            actualizar_datos_historicos(ticker, datos_historicos)

    print("[DEBUG] Iniciando actualización inicial de VolumenActual...")
    for ticker, _ in tickers_fechas:
        volumen_actual = scrapear_volumen_actual(ticker)
        if volumen_actual is not None:
            actualizar_volumen_actual(ticker, volumen_actual)

    print("[DEBUG] Ejecutando procedimiento almacenado inicial...")
    ejecutar_procedimiento()

    print("[DEBUG] Iniciando actualización periódica de VolumenActual cada hora en segundo plano...")
    hilo_volumen = threading.Thread(target=actualizar_volumen_continuo, args=(3600,), daemon=True)
    hilo_volumen.start()

if __name__ == "__main__":
    main()