import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import requests
from bs4 import BeautifulSoup
from datetime import datetime
from Base_Datos import conectar, leer_datos
import time

# Función para scrapear noticias de Seeking Alpha
def buscar_noticias_seekingalpha(ticker, fecha_deseada):
    try:
        url = f"https://seekingalpha.com/symbol/{ticker}/news"
        print(f"[DEBUG] URL generada: {url}")
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        response = requests.get(url, headers=headers)
        print(f"[DEBUG] Código de respuesta: {response.status_code}")
        if response.status_code != 200:
            print(f"[DEBUG] Error al conectar a Seeking Alpha para {ticker}: {response.status_code}")
            return None
        
        soup = BeautifulSoup(response.text, "html.parser")
        noticias = []
        
        # Buscar elementos de noticias (estructura basada en Seeking Alpha, abril 2025)
        for item in soup.select("article"):
            try:
                titulo_elem = item.select_one("h3 a")
                fecha_elem = item.select_one("span[itemprop='datePublished']")
                
                if not (titulo_elem and fecha_elem):
                    continue
                
                titulo = titulo_elem.text.strip()
                enlace = "https://seekingalpha.com" + titulo_elem["href"]
                fecha_texto = fecha_elem.text.strip()
                
                # Parsear la fecha (formato típico: "Apr 02, 2022")
                try:
                    fecha_publicacion = datetime.strptime(fecha_texto, "%b %d, %Y")
                except ValueError:
                    print(f"[DEBUG] No se pudo parsear fecha: {fecha_texto}")
                    continue
                
                # Tolerancia de ±7 días
                if abs((fecha_publicacion - fecha_deseada).days) <= 7:
                    print(f"[DEBUG] Noticia encontrada para {ticker} - Fecha: {fecha_publicacion}")
                    return {
                        "titulo": titulo,
                        "enlace": enlace,
                        "fecha_publicacion": fecha_publicacion
                    }
                
                noticias.append({
                    "titulo": titulo,
                    "enlace": enlace,
                    "fecha_publicacion": fecha_publicacion
                })
            except Exception as e:
                print(f"[DEBUG] Error al procesar elemento para {ticker}: {e}")
                continue
        
        if not noticias:
            print(f"[DEBUG] No se encontraron noticias para {ticker} en la página")
            return None
        
        # Si no hay coincidencia exacta, devolver la más cercana (opcional)
        noticia_cercana = min(noticias, key=lambda x: abs((x["fecha_publicacion"] - fecha_deseada).days), default=None)
        if noticia_cercana and abs((noticia_cercana["fecha_publicacion"] - fecha_deseada).days) <= 30:
            print(f"[DEBUG] Noticia más cercana para {ticker} - Fecha: {noticia_cercana['fecha_publicacion']}")
            return noticia_cercana
        
        print(f"[DEBUG] No hay noticias cercanas a {fecha_deseada} para {ticker}")
        return None
    
    except Exception as e:
        print(f"[DEBUG] Excepción al scrapear Seeking Alpha para {ticker}: {e}")
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

# Prueba con 10 tickers
if __name__ == "__main__":
    print("Iniciando prueba de scraping de noticias desde Seeking Alpha...")
    
    tickers_fechas = obtener_tickers_y_fechas(limite=10)
    if not tickers_fechas:
        print("No hay tickers para procesar.")
        sys.exit()

    for ticker, fecha in tickers_fechas:
        print(f"\nProbando {ticker} para la fecha {fecha}:")
        noticia = buscar_noticias_seekingalpha(ticker, fecha)
        if noticia:
            print(f"Título: {noticia['titulo']}")
            print(f"Enlace: {noticia['enlace']}")
            print(f"Fecha de publicación: {noticia['fecha_publicacion']}")
        else:
            print(f"No se encontraron noticias para {ticker} en o cerca de {fecha}")
        time.sleep(5)  # Pausa para evitar bloqueos

    print("\nPrueba completada.")