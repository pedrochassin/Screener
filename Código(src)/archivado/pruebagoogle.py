import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import yfinance as yf
from datetime import datetime
from Base_Datos import conectar, leer_datos
import time

# Función para obtener noticias con yfinance
def obtener_noticias_yfinance(ticker, fecha_deseada):
    try:
        stock = yf.Ticker(ticker)
        noticias = stock.news
        if not noticias:
            print(f"[DEBUG] No se encontraron noticias para {ticker}")
            return None
        
        # Convertir fecha deseada a timestamp UNIX
        fecha_deseada_ts = int(fecha_deseada.timestamp())
        
        # Buscar noticia más cercana a la fecha deseada (tolerancia de ±7 días para probar)
        noticia_cercana = None
        menor_diferencia = float('inf')
        
        for noticia in noticias:
            fecha_publicacion_ts = noticia.get("providerPublishTime")
            if fecha_publicacion_ts:
                diferencia = abs(fecha_publicacion_ts - fecha_deseada_ts)
                if diferencia < menor_diferencia and diferencia <= 604800:  # 604800 segundos = 7 días
                    menor_diferencia = diferencia
                    noticia_cercana = {
                        "titulo": noticia["title"],
                        "enlace": noticia["link"],
                        "fecha_publicacion": datetime.fromtimestamp(fecha_publicacion_ts)
                    }
        
        if noticia_cercana:
            print(f"[DEBUG] Noticia encontrada para {ticker} - Fecha: {noticia_cercana['fecha_publicacion']}")
            return noticia_cercana
        else:
            print(f"[DEBUG] No hay noticias cercanas a {fecha_deseada} para {ticker}")
            return None
    
    except Exception as e:
        print(f"[DEBUG] Error al obtener noticias para {ticker}: {e}")
        return None

# Obtener 10 tickers y fechas de la base de datos
def obtener_tickers_y_fechas(limite=10):
    conn = conectar()
    if not conn:
        print("[DEBUG] No se pudo conectar a la base de datos")
        return []
    try:
        cursor = conn.cursor()
        query = """
        SELECT TOP %d [Fecha], [Ticker]
        FROM [TablaFinviz]
        WHERE [Noticia] IS NULL OR [Noticia] = ''
        """
        cursor.execute(query % limite)
        datos = cursor.fetchall()
        tickers_fechas = [(row[1], row[0]) for row in datos]
        print(f"[DEBUG] Obtenidos {len(tickers_fechas)} tickers y fechas desde TablaFinviz")
        return tickers_fechas
    except Exception as e:
        print(f"[DEBUG] Error al leer tickers: {e}")
        return []
    finally:
        conn.close()

# Actualizar noticia en la base (opcional, para la prueba solo mostramos)
def actualizar_noticia(conn, ticker, noticia, fecha):
    try:
        cursor = conn.cursor()
        noticia_texto = f"{noticia['titulo']} (Enlace: {noticia['enlace']})"
        query = "UPDATE [TablaFinviz] SET [Noticia] = ? WHERE [Ticker] = ? AND [Fecha] = ?"
        valores = (noticia_texto, ticker, fecha.strftime("%Y-%m-%d") if isinstance(fecha, datetime) else fecha)
        cursor.execute(query, valores)
        conn.commit()
        print(f"[DEBUG] Noticia actualizada para {ticker} en {fecha}")
    except Exception as e:
        print(f"[DEBUG] Error al actualizar noticia: {e}")
    finally:
        cursor.close()

# Prueba con 10 tickers
if __name__ == "__main__":
    print("Iniciando prueba de noticias con yfinance...")
    
    tickers_fechas = obtener_tickers_y_fechas(limite=10)
    if not tickers_fechas:
        print("No hay tickers para procesar.")
        sys.exit()

    conn = conectar()
    if not conn:
        print("[DEBUG] No se pudo conectar a la base para actualizar")
        sys.exit()

    for ticker, fecha in tickers_fechas:
        print(f"\nProbando {ticker} para la fecha {fecha}:")
        noticia = obtener_noticias_yfinance(ticker, fecha)
        if noticia:
            print(f"Título: {noticia['titulo']}")
            print(f"Enlace: {noticia['enlace']}")
            print(f"Fecha de publicación: {noticia['fecha_publicacion']}")
            # Descomentar la siguiente línea si quieres actualizar la base
            # actualizar_noticia(conn, ticker, noticia, fecha)
        else:
            print(f"No se encontraron noticias para {ticker} en o cerca de {fecha}")
        time.sleep(1)  # Pausa ligera para no saturar la API

    conn.close()
    print("\nPrueba completada.")