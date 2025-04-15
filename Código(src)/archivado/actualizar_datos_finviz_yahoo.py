import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import yfinance as yf
import requests
from bs4 import BeautifulSoup
from Base_Datos import conectar, leer_datos, actualizar_multiples
from scraper import obtener_datos_adicionales, obtener_noticias
from utils import convertir_volumen
from datetime import datetime, timedelta, date
from deep_translator import GoogleTranslator

# Inicializar el traductor
translator = GoogleTranslator(source='auto', target='es')

# Traducir texto al español
def traducir_texto(texto):
    try:
        traduccion = translator.translate(texto)
        return traduccion
    except Exception as e:
        print(f"[DEBUG] Error al traducir texto: {e}")
        return texto

# Nueva función para obtener noticias por fecha
def obtener_noticias_por_fecha(ticker, fecha_objetivo):
    """Obtiene noticias de Finviz y devuelve la que coincide con la fecha objetivo."""
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"}
    url = f"https://finviz.com/quote.ashx?t={ticker}&p=d"
    print(f"[DEBUG] Solicitando noticias de Finviz para {ticker}: {url}")
    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"[DEBUG] Error al conectar a Finviz para {ticker}: {response.status_code}")
            return None
        
        soup = BeautifulSoup(response.text, "lxml")
        table = soup.find("table", {"id": "news-table"})
        if not table:
            print(f"[DEBUG] No se encontró tabla de noticias para {ticker}")
            return None
        
        # Convertir fecha_objetivo a datetime.date si es string
        if isinstance(fecha_objetivo, str):
            fecha_objetivo = datetime.strptime(fecha_objetivo, "%Y-%m-%d").date()
        
        for row in table.find_all("tr"):
            columns = row.find_all("td")
            if len(columns) >= 2:
                fecha_str = columns[0].text.strip()
                link_element = columns[1].find("a")
                titular = link_element.text.strip() if link_element else columns[1].text.strip()
                enlace = link_element["href"] if link_element else "No hay enlace"
                
                # Parsear la fecha de la noticia, ignorando horas
                try:
                    if "Today" in fecha_str:
                        fecha_noticia = datetime.today().date()
                    elif " " in fecha_str:  # Formato con fecha y hora: "Aug-03-23 02:43PM"
                        fecha_noticia = datetime.strptime(fecha_str.split(" ")[0], "%b-%d-%y").date()
                    else:  # Solo hora: "02:43AM" (noticia de hoy)
                        fecha_noticia = datetime.today().date()
                        print(f"[DEBUG] Hora detectada para {ticker}, asumiendo fecha actual: {fecha_noticia}")
                except ValueError:
                    print(f"[DEBUG] No se pudo parsear fecha: {fecha_str}")
                    continue
                
                # Comparar con la fecha objetivo
                if fecha_noticia == fecha_objetivo:
                    titular_es = traducir_texto(titular)
                    print(f"[DEBUG] Noticia encontrada para {ticker} en {fecha_objetivo}: {titular}")
                    return f"{titular_es} {enlace}"
        
        print(f"[DEBUG] No se encontró noticia para {ticker} en {fecha_objetivo}")
        return "No se encontraron noticias para esta fecha."
    except Exception as e:
        print(f"[DEBUG] Error al obtener noticias para {ticker}: {e}")
        return None

# Obtener tickers y fechas
def obtener_tickers_y_fechas():
    conn = conectar()
    if not conn:
        print("No se pudo conectar a la base.")
        return []
    try:
        datos = leer_datos(conn, "TablaFinviz")
        tickers_fechas = [(row[1], row[0]) for row in datos]
        print(f"[DEBUG] Obtenidos {len(tickers_fechas)} tickers y fechas desde TablaFinviz")
        return tickers_fechas
    except Exception as e:
        print(f"[DEBUG] Error al leer tickers y fechas: {e}")
        return []
    finally:
        conn.close()

# Obtener volumen del día
def obtener_volumen_dia(ticker, fecha):
    try:
        stock = yf.Ticker(ticker)
        if isinstance(fecha, str):
            fecha = datetime.strptime(fecha, "%Y-%m-%d")
        hist = stock.history(start=fecha, end=fecha + timedelta(days=1), interval="1d")
        if hist.empty or 'Volume' not in hist.columns or hist['Volume'].isnull().all():
            print(f"[DEBUG] No se encontraron datos para {ticker} en {fecha}")
            return None
        volumen = int(hist['Volume'].iloc[0])
        print(f"[DEBUG] Volumen del día para {ticker} en {fecha}: {volumen}")
        return volumen
    except Exception as e:
        print(f"[DEBUG] Error al obtener volumen para {ticker} en {fecha}: {e}")
        return None

# Obtener volumen promedio de 50 días
def obtener_avg_volume_historico(ticker, fecha):
    try:
        stock = yf.Ticker(ticker)
        if isinstance(fecha, str):
            fecha = datetime.strptime(fecha, "%Y-%m-%d")
        fecha_inicio = fecha - timedelta(days=50)
        hist = stock.history(start=fecha_inicio, end=fecha, interval="1d")
        if hist.empty or 'Volume' not in hist.columns or hist['Volume'].isnull().all():
            print(f"[DEBUG] No se encontraron datos históricos para {ticker} entre {fecha_inicio} y {fecha}")
            return None
        avg_volume = int(hist['Volume'].mean())
        print(f"[DEBUG] AvgVolume (50 días) para {ticker} hasta {fecha}: {avg_volume}")
        return avg_volume
    except Exception as e:
        print(f"[DEBUG] Error al calcular AvgVolume para {ticker}: {e}")
        return None

# Actualizar Volumen
def actualizar_volumen(conn, ticker, volumen, fecha):
    try:
        cursor = conn.cursor()
        volumen_formateado = f"{volumen:,}" if volumen is not None else None
        query = "UPDATE [TablaFinviz] SET [Volumen] = ? WHERE [Ticker] = ? AND [Fecha] = ?"
        valores = (volumen_formateado, ticker, fecha.strftime("%Y-%m-%d") if isinstance(fecha, datetime) else fecha)
        cursor.execute(query, valores)
        conn.commit()
        print(f"[DEBUG] Volumen actualizado para {ticker} en {fecha}: {volumen_formateado}")
    except Exception as e:
        print(f"[DEBUG] Error al actualizar Volumen para {ticker}: {e}")
    finally:
        cursor.close()

# Actualizar AvgVolume
def actualizar_avg_volume(conn, ticker, avg_volume, fecha):
    try:
        cursor = conn.cursor()
        avg_volume_formateado = f"{avg_volume:,}" if avg_volume is not None else None
        query = "UPDATE [TablaFinviz] SET [AvgVolume] = ? WHERE [Ticker] = ? AND [Fecha] = ?"
        valores = (avg_volume_formateado, ticker, fecha.strftime("%Y-%m-%d") if isinstance(fecha, datetime) else fecha)
        cursor.execute(query, valores)
        conn.commit()
        print(f"[DEBUG] AvgVolume actualizado para {ticker} en {fecha}: {avg_volume_formateado}")
    except Exception as e:
        print(f"[DEBUG] Error al actualizar AvgVolume para {ticker}: {e}")
    finally:
        cursor.close()

# Actualizar Noticia
def actualizar_noticia(conn, ticker, noticia, fecha):
    try:
        cursor = conn.cursor()
        if isinstance(noticia, dict):
            noticia_texto = f"{noticia['titulo_es']} (Fuente: {noticia['fuente']}, Enlace: {noticia['enlace']}"
        elif isinstance(noticia, str):
            parts = noticia.rsplit(" ", 1)
            if len(parts) == 2:
                titular = parts[0]
                enlace = parts[1]
                titular_es = traducir_texto(titular)
                noticia_texto = f"{titular_es} (Fuente: Finviz, Enlace: {enlace}"
            else:
                noticia_texto = noticia
        else:
            raise ValueError(f"Tipo de noticia no soportado: {type(noticia)}")
        
        query = "UPDATE [TablaFinviz] SET [Noticia] = ? WHERE [Ticker] = ? AND [Fecha] = ?"
        valores = (noticia_texto, ticker, fecha.strftime("%Y-%m-%d") if isinstance(fecha, datetime) else fecha)
        cursor.execute(query, valores)
        conn.commit()
        print(f"[DEBUG] Noticia actualizada para {ticker} en {fecha}: {noticia_texto}")
    except Exception as e:
        print(f"[DEBUG] Error al actualizar noticia para {ticker}: {e}")
    finally:
        cursor.close()

# Verificar si los datos ya existen
def datos_existen(conn, ticker, fecha, columna):
    try:
        cursor = conn.cursor()
        query = f"SELECT [{columna}] FROM [TablaFinviz] WHERE [Ticker] = ? AND [Fecha] = ?"
        valores = (ticker, fecha.strftime("%Y-%m-%d") if isinstance(fecha, datetime) else fecha)
        cursor.execute(query, valores)
        resultado = cursor.fetchone()
        cursor.close()
        return resultado is not None and resultado[0] is not None and resultado[0] != ""
    except Exception as e:
        print(f"[DEBUG] Error al verificar {columna} para {ticker} en {fecha}: {e}")
        return False

# Verificar datos de Finviz
def datos_finviz_existen(conn, ticker, fecha):
    try:
        cursor = conn.cursor()
        query = """
        SELECT [ShsFloat], [ShortFloat], [ShortRatio], [CashSh]
        FROM [TablaFinviz]
        WHERE [Ticker] = ? AND [Fecha] = ?
        """
        valores = (ticker, fecha.strftime("%Y-%m-%d") if isinstance(fecha, datetime) else fecha)
        cursor.execute(query, valores)
        resultado = cursor.fetchone()
        cursor.close()
        if resultado is None:
            return False
        return all(val is not None and val != "" for val in resultado)
    except Exception as e:
        print(f"[DEBUG] Error al verificar datos de Finviz para {ticker} en {fecha}: {e}")
        return False

# Función principal
def actualizar_datos_finviz_yahoo():
    print(f"Iniciando actualización de datos a las {datetime.now().strftime('%H:%M:%S')}...")
    
    tickers_fechas = obtener_tickers_y_fechas()
    if not tickers_fechas:
        print("No se encontraron tickers para procesar.")
        return

    conn = conectar()
    if not conn:
        print("No se pudo conectar a la base. Terminando.")
        return

    for ticker, fecha in tickers_fechas:
        try:
            # Datos de Finviz (solo si no existen)
            if not datos_finviz_existen(conn, ticker, fecha):
                datos_ad = obtener_datos_adicionales(ticker)
                print(f"[DEBUG] Datos obtenidos de Finviz para {ticker}: {datos_ad}")
                if datos_ad:
                    shs_float = convertir_volumen(datos_ad.get("Shs Float", ""))
                    short_float = datos_ad.get("Short Float")
                    short_ratio = datos_ad.get("Short Ratio")
                    cash_sh = datos_ad.get("Cash/sh")
                    print(f"[DEBUG] Valores extraídos - Shs Float: {shs_float}, Short Float: {short_float}, Short Ratio: {short_ratio}, Cash/sh: {cash_sh}")
                else:
                    shs_float, short_float, short_ratio, cash_sh = None, None, None, None
                    print(f"[DEBUG] No se obtuvieron datos adicionales para {ticker}")
                valores = (shs_float, short_float, short_ratio, None, cash_sh)
                condicion = f"Ticker = '{ticker}' AND Fecha = '{fecha}'"
                actualizar_multiples(conn, "TablaFinviz", valores, condicion)
                print(f"[DEBUG] Actualizados datos de Finviz para {ticker} en {fecha}")
            else:
                print(f"[DEBUG] Datos de Finviz ya existen para {ticker} en {fecha}, omitiendo...")

            # Volumen del día (solo si no existe)
            if not datos_existen(conn, ticker, fecha, "Volumen"):
                volumen_dia = obtener_volumen_dia(ticker, fecha)
                if volumen_dia is not None:
                    actualizar_volumen(conn, ticker, volumen_dia, fecha)
            else:
                print(f"[DEBUG] Volumen ya existe para {ticker} en {fecha}, omitiendo...")

            # AvgVolume histórico (solo si no existe)
            if not datos_existen(conn, ticker, fecha, "AvgVolume"):
                avg_volume = obtener_avg_volume_historico(ticker, fecha)
                if avg_volume is not None:
                    actualizar_avg_volume(conn, ticker, avg_volume, fecha)
            else:
                print(f"[DEBUG] AvgVolume ya existe para {ticker} en {fecha}, omitiendo...")

            # Noticias desde Finviz (solo si no existe)
            if not datos_existen(conn, ticker, fecha, "Noticia"):
                noticia = obtener_noticias_por_fecha(ticker, fecha)
                print(f"[DEBUG] Noticia obtenida para {ticker}: {noticia} (tipo: {type(noticia)})")
                if noticia and noticia != "No se encontraron noticias para esta fecha.":
                    actualizar_noticia(conn, ticker, noticia, fecha)
                else:
                    print(f"[DEBUG] No se actualizó noticia para {ticker} en {fecha}")
            else:
                print(f"[DEBUG] Noticia ya existe para {ticker} en {fecha}, omitiendo...")

        except Exception as e:
            print(f"[DEBUG] Error al procesar {ticker} en {fecha}: {e}")

    conn.close()
    print("Actualización de datos completada.")

if __name__ == "__main__":
    actualizar_datos_finviz_yahoo()