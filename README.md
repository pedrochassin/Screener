# Screener 2025

**Screener 2025** es un programa en Python que scrapea datos financieros de [Finviz](https://finviz.com/), los guarda en una base de datos SQL Server, busca noticias relacionadas con los tickers obtenidos, las traduce al español, y actualiza la base con datos adicionales como volumen promedio y flotación corta. Este proyecto está diseñado para ser modular, portátil y fácil de mantener.

## Características
- **Scraping de Finviz**: Extrae la tabla de "ganadores" desde la página principal de Finviz usando Selenium.
- **Almacenamiento en SQL Server**: Guarda los datos en la tabla `TablaFinviz` en la base de datos `FinvizData`.
- **Búsqueda de noticias**: Encuentra noticias para tickers sin información usando BeautifulSoup, las traduce al español con `deep_translator`, y las guarda.
- **Datos adicionales**: Obtiene estadísticas como "Shs Float", "Short Float", etc., y actualiza la tabla.
- **Estructura modular**: Divide el código en archivos (`Base_Datos.py`, `scraper.py`, `utils.py`, `main.py`) para facilitar modificaciones.

## Requisitos
- **Sistema operativo**: Windows (probado en Windows 10/11).
- **Python**: Versión 3.8 o superior.
- **SQL Server**: Configurado con una base de datos llamada `FinvizData` y una tabla `TablaFinviz`.
- **Chrome**: Necesario para Selenium (ChromeDriver debe coincidir con la versión instalada).
- **Dependencias**: Listadas en `lista.txt`.

### Estructura de la tabla `TablaFinviz`
La tabla en SQL Server debe tener estas columnas:
```sql
CREATE TABLE TablaFinviz (
    Fecha DATE,
    Ticker VARCHAR(10),
    Precio VARCHAR(20),
    CambioPorcentaje VARCHAR(20),
    Volumen VARCHAR(20),
    Vacío VARCHAR(20),
    Categoria VARCHAR(50),
    Noticia TEXT,
    ShsFloat VARCHAR(20),
    ShortFloat VARCHAR(20),
    ShortRatio VARCHAR(20),
    AvgVolume VARCHAR(20),
    CashSh VARCHAR(20)
);
