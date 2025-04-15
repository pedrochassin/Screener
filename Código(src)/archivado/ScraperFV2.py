import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import datetime
import pyodbc

def conectar_sql_server():
    """Conecta a SQL Server con manejo de errores."""
    try:
        conn = pyodbc.connect(
            'DRIVER={SQL Server};'
            'SERVER=Pedro;'
            'DATABASE=FinvizData;'
            'UID=sa;'
            'PWD=1593Satriani;'
        )
        return conn
    except pyodbc.Error as e:
        print(f"Error al conectar a SQL Server: {e}")
        raise

def obtener_registros_nuevos(conn):
    """Obtiene registros donde las columnas adicionales están vacías."""
    with conn.cursor() as cursor:
        query = """
            SELECT Ticker, Fecha
            FROM TablaFinviz
            WHERE (Noticia IS NULL OR Precio IS NULL OR CambioPorcentaje IS NULL OR 
                   Volumen IS NULL OR AvgVolume IS NULL OR ShsFloat IS NULL OR 
                   ShortRatio IS NULL OR CashSh IS NULL OR ShortFloat IS NULL)
        """
        cursor.execute(query)
        registros = [(row.Ticker, row.Fecha) for row in cursor.fetchall()]
    return registros

def configurar_navegador():
    """Configura Selenium en modo headless."""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--log-level=3")
    chrome_options.add_argument("--window-size=1920x1080")
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def obtener_noticia_para_fecha(ticker, fecha_objetivo):
    """Busca la noticia que coincida con la fecha del ticker o la más cercana."""
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"}
    url = f"https://finviz.com/quote.ashx?t={ticker}&p=d"
    
    if isinstance(fecha_objetivo, str):
        fecha_objetivo = datetime.datetime.strptime(fecha_objetivo, "%Y-%m-%d").date()
    
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "lxml")
        table = soup.find("table", {"id": "news-table"})
        if table:
            noticias = []
            for row in table.find_all("tr"):
                columns = row.find_all("td")
                if len(columns) >= 2:
                    noticia_fecha_texto = columns[0].text.strip()
                    noticia_fecha = None
                    try:
                        if "Today" in noticia_fecha_texto:
                            noticia_fecha = datetime.datetime.today().date()
                        elif "Yesterday" in noticia_fecha_texto:
                            noticia_fecha = datetime.datetime.today().date() - datetime.timedelta(days=1)
                        else:
                            noticia_fecha = datetime.datetime.strptime(noticia_fecha_texto, "%b-%d-%y").date()
                    except ValueError:
                        continue

                    link_element = columns[1].find("a")
                    texto = link_element.text.strip() if link_element else columns[1].text.strip()
                    link = link_element["href"] if link_element else "No hay enlace"
                    noticias.append((noticia_fecha, texto, link))
            
            noticia_mas_cercana = None
            diferencia_minima = float("inf")
            for noticia_fecha, texto, link in noticias:
                diferencia = abs((noticia_fecha - fecha_objetivo).days)
                if diferencia < diferencia_minima:
                    diferencia_minima = diferencia
                    noticia_mas_cercana = (texto, link)

            if noticia_mas_cercana:
                return f"{noticia_mas_cercana[0]} {noticia_mas_cercana[1]}"
    return "No se encontraron noticias."

def convertir_valor_abreviado(valor):
    """Convierte valores abreviados (ej. 12.71M) o notación científica (ej. 1.271e+007) a números completos con separadores de miles."""
    if valor in [None, "N/A", ""]:
        return None
    
    try:
        valor = valor.replace(",", "").strip()
        # Primero intentamos convertir directamente como número (incluye notación científica)
        try:
            numero = float(valor)
        except ValueError:
            # Si falla, asumimos que tiene una letra al final (K, M, B)
            if valor[-1].upper() == "K":
                numero = float(valor[:-1]) * 1_000
            elif valor[-1].upper() == "M":
                numero = float(valor[:-1]) * 1_000_000
            elif valor[-1].upper() == "B":
                numero = float(valor[:-1]) * 1_000_000_000
            else:
                raise ValueError("Formato no reconocido")
        return "{:,.0f}".format(numero)
    except (ValueError, TypeError):
        return None

def formatear_numero(valor):
    """Convierte un número (incluyendo notación científica) a formato con separadores de miles."""
    if valor in [None, "N/A", ""]:
        return None
    
    try:
        numero = float(valor)
        return "{:,.0f}".format(numero)
    except (ValueError, TypeError):
        return None

def obtener_datos_adicionales(ticker, fecha_objetivo):
    """Scrapea datos adicionales de Finviz."""
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"}
    url = f"https://finviz.com/quote.ashx?t={ticker}&p=d"

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "lxml")
        datos = {}
        tabla_principal = soup.find("table", class_="snapshot-table2")
        if tabla_principal:
            rows = tabla_principal.find_all("tr")
            for row in rows:
                columns = row.find_all("td")
                if len(columns) >= 12:
                    for i in range(0, 12, 2):
                        key = columns[i].text.strip()
                        value = columns[i+1].text.strip()
                        if key == "Price":
                            datos["Precio"] = value
                        elif key == "Change":
                            datos["CambioPorcentaje"] = value
                        elif key == "Volume":
                            datos["Volumen"] = formatear_numero(value)
                        elif key == "Avg Volume":
                            datos["AvgVolume"] = formatear_numero(value)
                        elif key == "Shs Float":
                            datos["ShsFloat"] = convertir_valor_abreviado(value)
                        elif key == "Short Ratio":
                            datos["ShortRatio"] = value
                        elif key == "Cash/sh":
                            datos["CashSh"] = value
                        elif key == "Short Float":
                            datos["ShortFloat"] = value  # Nuevo campo añadido
        return datos
    return {}

def validar_valor_numerico(valor):
    """Valida si el valor es un número válido."""
    if valor in [None, "N/A", ""]:
        return None
    try:
        return float(valor.replace(',', '').replace('$', '').replace('%', '').strip())
    except (ValueError, TypeError):
        return None

def actualizar_base_datos(conn, ticker, fecha_objetivo, noticia, datos_adicionales):
    """Actualiza la base de datos con los datos obtenidos."""
    with conn.cursor() as cursor:
        precio = validar_valor_numerico(datos_adicionales.get("Precio", "N/A"))
        cambio_porcentaje = validar_valor_numerico(datos_adicionales.get("CambioPorcentaje", "N/A"))
        volumen = validar_valor_numerico(datos_adicionales.get("Volumen", "N/A"))
        avg_volumen = validar_valor_numerico(datos_adicionales.get("AvgVolume", "N/A"))
        shs_float = validar_valor_numerico(datos_adicionales.get("ShsFloat", "N/A"))
        short_ratio = validar_valor_numerico(datos_adicionales.get("ShortRatio", "N/A"))
        cash_sh = validar_valor_numerico(datos_adicionales.get("CashSh", "N/A"))
        short_float = validar_valor_numerico(datos_adicionales.get("ShortFloat", "N/A"))

        query = """
            UPDATE TablaFinviz
            SET Noticia = ?, Precio = ?, CambioPorcentaje = ?, Volumen = ?, AvgVolume = ?, 
                ShsFloat = ?, ShortRatio = ?, CashSh = ?, ShortFloat = ?
            WHERE Ticker = ? AND Fecha = ?
        """
        cursor.execute(query, (
            noticia,
            precio,
            cambio_porcentaje,
            volumen,
            avg_volumen,
            shs_float,
            short_ratio,
            cash_sh,
            short_float,
            ticker,
            fecha_objetivo
        ))
        conn.commit()

def main():
    try:
        conn = conectar_sql_server()
        registros_nuevos = obtener_registros_nuevos(conn)
        driver = configurar_navegador()

        for ticker, fecha_objetivo in registros_nuevos:
            print(f"Procesando {ticker} para la fecha {fecha_objetivo}")
            noticia = obtener_noticia_para_fecha(ticker, fecha_objetivo)
            datos_adicionales = obtener_datos_adicionales(ticker, fecha_objetivo)
            actualizar_base_datos(conn, ticker, fecha_objetivo, noticia, datos_adicionales)

        driver.quit()
        conn.close()
    except Exception as e:
        print(f"Error en la ejecución del programa: {e}")
        if 'conn' in locals():
            conn.close()
        if 'driver' in locals():
            driver.quit()

if __name__ == "__main__":
    main()