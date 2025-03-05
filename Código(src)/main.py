from Base_Datos import conectar, leer_datos, insertar_datos, actualizar_datos, actualizar_multiples
from scraper import configurar_navegador, obtener_tabla_finviz, obtener_noticias, obtener_datos_adicionales
from utils import convertir_volumen, traducir_texto, obtener_fecha_actual

print("Iniciando proceso...")

# Conectar a la base de datos
conn = conectar()
if not conn:
    print("No se pudo conectar a la base. Terminando.")
    exit()

# Scrapear tabla de Finviz
driver = configurar_navegador()
datos_tabla = obtener_tabla_finviz(driver)
driver.quit()

# Guardar datos en TablaFinviz
for datos in datos_tabla:
    volumen_convertido = convertir_volumen(datos[3])
    valores = (obtener_fecha_actual(), datos[0], datos[1], datos[2], volumen_convertido, datos[4], datos[5], None)
    insertar_datos(conn, "TablaFinviz", valores)

# Obtener tickers sin noticias
tickers_sin_noticias = [row[1] for row in leer_datos(conn, "TablaFinviz", "Noticia IS NULL OR Noticia = ''")]

# Actualizar noticias
for ticker in tickers_sin_noticias:
    noticia_en = obtener_noticias(ticker)
    noticia_es = traducir_texto(noticia_en.split(" (")[0]) + " (" + noticia_en.split(" (")[1] if "(" in noticia_en else noticia_en
    actualizar_datos(conn, "TablaFinviz", "Noticia", noticia_es, f"Ticker = '{ticker}'")

# Obtener tickers sin datos adicionales
tickers_sin_datos = [row[1] for row in leer_datos(conn, "TablaFinviz", "ShsFloat IS NULL OR ShortFloat IS NULL OR ShortRatio IS NULL OR AvgVolume IS NULL OR CashSh IS NULL")]

# Actualizar datos adicionales
for ticker in tickers_sin_datos:
    datos_ad = obtener_datos_adicionales(ticker)
    if datos_ad:
        valores = (
            convertir_volumen(datos_ad.get("Shs Float", "")),
            datos_ad.get("Short Float"),
            datos_ad.get("Short Ratio"),
            convertir_volumen(datos_ad.get("Avg Volume", "")),
            datos_ad.get("Cash/sh")
        )
        actualizar_multiples(conn, "TablaFinviz", valores, f"Ticker = '{ticker}'")

conn.close()
print("Proceso completado.")