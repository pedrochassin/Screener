import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def configurar_navegador():
    """Configura Selenium en modo headless."""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--log-level=3")
    chrome_options.add_argument("--window-size=1920x1080")
    chrome_options.add_argument("start-maximized")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36")
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def obtener_tabla_finviz(driver):
    """Scrape la tabla de ganadores desde Finviz."""
    try:
        driver.set_page_load_timeout(180)
        driver.get("https://finviz.com/")
        tabla = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="homepage"]/table/tbody/tr[2]/td/table/tbody/tr/td[1]/table'))
        )
        filas = tabla.find_elements(By.TAG_NAME, "tr")
        datos = []
        for fila in filas:
            columnas = fila.find_elements(By.TAG_NAME, "td")
            if columnas:
                datos.append([columna.text for columna in columnas])
        return datos
    except Exception as e:
        print(f"Error al scrapear tabla: {e}")
        return []

def obtener_noticias(ticker):
    """Scrape noticias de Finviz para un ticker."""
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"}
    url = f"https://finviz.com/quote.ashx?t={ticker}&p=d"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "lxml")
        table = soup.find("table", {"id": "news-table"})
        if table:
            row = table.find("tr")
            if row:
                columns = row.find_all("td")
                if len(columns) >= 2:
                    link_element = columns[1].find("a")
                    texto = link_element.text.strip() if link_element else columns[1].text.strip()
                    link = "https://finviz.com" + link_element["href"] if link_element else "No hay enlace"
                    return f"{texto} ({link})"
    return "No se encontraron noticias."

def obtener_datos_adicionales(ticker):
    """Scrape datos adicionales de Finviz."""
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"}
    url = f"https://finviz.com/quote.ashx?t={ticker}&p=d"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "lxml")
        datos = {}
        estadisticas = soup.find_all("table", class_="snapshot-table2")
        if estadisticas:
            for table in estadisticas:
                rows = table.find_all("tr")
                for row in rows:
                    columns = row.find_all("td")
                    if len(columns) == 12:
                        for i in range(0, 12, 2):
                            key = columns[i].text.strip()
                            value = columns[i+1].text.strip()
                            if key in ["Shs Float", "Short Float", "Short Ratio", "Avg Volume", "Cash/sh"]:
                                datos[key] = value
        return datos
    return {}