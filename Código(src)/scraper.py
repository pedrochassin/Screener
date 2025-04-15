import requests
# Importa la biblioteca requests para realizar solicitudes HTTP.

from bs4 import BeautifulSoup
# Importa BeautifulSoup para analizar y extraer datos de HTML.

from selenium import webdriver
# Importa Selenium para automatizar la interacción con navegadores web.

from selenium.webdriver.common.by import By
# Importa selectores para localizar elementos en el DOM.

from selenium.webdriver.chrome.options import Options
# Importa opciones para configurar el navegador Chrome.

from selenium.webdriver.support.ui import WebDriverWait
# Importa WebDriverWait para esperar a que elementos estén disponibles.

from selenium.webdriver.support import expected_conditions as EC
# Importa condiciones esperadas para esperar eventos específicos.

def configurar_navegador():
    """Configura Selenium en modo headless."""
    chrome_options = Options()
    # Crea un objeto de opciones para el navegador Chrome.
    chrome_options.add_argument("--headless")
    # Ejecuta el navegador en modo sin interfaz gráfica.
    chrome_options.add_argument("--disable-gpu")
    # Desactiva el uso de GPU para mejorar compatibilidad.
    chrome_options.add_argument("--log-level=3")
    # Reduce el nivel de registro para evitar mensajes innecesarios.
    chrome_options.add_argument("--window-size=1920x1080")
    # Establece el tamaño de la ventana del navegador.
    chrome_options.add_argument("start-maximized")
    # Inicia el navegador maximizado.
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36")
    # Establece un agente de usuario personalizado.
    driver = webdriver.Chrome(options=chrome_options)
    # Crea una instancia del navegador Chrome con las opciones configuradas.
    return driver
    # Devuelve el objeto del navegador configurado.

def obtener_tabla_finviz(driver):
    """Scrape la tabla de ganadores desde Finviz."""
    try:
        driver.set_page_load_timeout(180)
        # Establece un tiempo máximo de espera para cargar la página.
        driver.get("https://finviz.com/")
        # Navega a la página principal de Finviz.
        tabla = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="homepage"]/table/tbody/tr[2]/td/table/tbody/tr/td[1]/table'))
        )
        # Espera hasta que la tabla esté presente en el DOM.
        filas = tabla.find_elements(By.TAG_NAME, "tr")
        # Encuentra todas las filas de la tabla.
        datos = []
        # Lista para almacenar los datos extraídos.
        for fila in filas:
            columnas = fila.find_elements(By.TAG_NAME, "td")
            # Encuentra todas las columnas en cada fila.
            if columnas:
                datos.append([columna.text for columna in columnas])
                # Extrae el texto de cada columna y lo agrega a la lista.
        return datos
        # Devuelve los datos extraídos de la tabla.
    except Exception as e:
        print(f"Error al scrapear tabla: {e}")
        # Imprime un mensaje de error si ocurre una excepción.
        return []
        # Devuelve una lista vacía en caso de error.

def obtener_noticias(ticker):
    """Scrape noticias de Finviz para un ticker."""
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"}
    # Define un encabezado de agente de usuario para la solicitud HTTP.
    url = f"https://finviz.com/quote.ashx?t={ticker}&p=d"
    # Construye la URL para el ticker específico.
    response = requests.get(url, headers=headers)
    # Realiza una solicitud HTTP GET a la URL.
    if response.status_code == 200:
        # Verifica si la solicitud fue exitosa.
        soup = BeautifulSoup(response.text, "lxml")
        # Analiza el contenido HTML de la respuesta.
        table = soup.find("table", {"id": "news-table"})
        # Busca la tabla de noticias en la página.
        if table:
            row = table.find("tr")
            # Encuentra la primera fila de la tabla.
            if row:
                columns = row.find_all("td")
                # Encuentra todas las columnas en la fila.
                if len(columns) >= 2:
                    link_element = columns[1].find("a")
                    # Busca un enlace en la segunda columna.
                    texto = link_element.text.strip() if link_element else columns[1].text.strip()
                    # Extrae el texto del enlace o de la columna.
                    link = "" + link_element["href"] if link_element else "No hay enlace"
                    # Extrae el enlace o devuelve un mensaje predeterminado.
                    return f"{texto} {link}"
                    # Devuelve el texto y el enlace concatenados.
    return "No se encontraron noticias."
    # Devuelve un mensaje predeterminado si no se encuentran noticias.

def obtener_datos_adicionales(ticker):
    """Scrape datos adicionales de Finviz."""
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"}
    # Define un encabezado de agente de usuario para la solicitud HTTP.
    url = f"https://finviz.com/quote.ashx?t={ticker}&p=d"
    # Construye la URL para el ticker específico.
    response = requests.get(url, headers=headers)
    # Realiza una solicitud HTTP GET a la URL.
    if response.status_code == 200:
        # Verifica si la solicitud fue exitosa.
        soup = BeautifulSoup(response.text, "lxml")
        # Analiza el contenido HTML de la respuesta.
        datos = {}
        # Diccionario para almacenar los datos extraídos.
        estadisticas = soup.find_all("table", class_="snapshot-table2")
        # Busca todas las tablas con la clase "snapshot-table2".
        if estadisticas:
            for table in estadisticas:
                rows = table.find_all("tr")
                # Encuentra todas las filas en la tabla.
                for row in rows:
                    columns = row.find_all("td")
                    # Encuentra todas las columnas en la fila.
                    if len(columns) == 12:
                        # Verifica si hay 12 columnas (pares clave-valor).
                        for i in range(0, 12, 2):
                            key = columns[i].text.strip()
                            # Extrae la clave (nombre del dato).
                            value = columns[i+1].text.strip()
                            # Extrae el valor asociado a la clave.
                            if key in ["Shs Float", "Short Float", "Short Ratio", "Avg Volume", "Cash/sh"]:
                                datos[key] = value
                                # Agrega el par clave-valor al diccionario.
        return datos
        # Devuelve el diccionario con los datos extraídos.
    return {}
    # Devuelve un diccionario vacío si no se encuentran datos.