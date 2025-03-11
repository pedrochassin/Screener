from Base_Datos import conectar, leer_datos, insertar_datos, actualizar_datos, actualizar_multiples
from scraper import configurar_navegador, obtener_tabla_finviz, obtener_noticias, obtener_datos_adicionales
from utils import convertir_volumen, traducir_texto, obtener_fecha_actual
import datetime

def buscar_tickers():
    """Función principal que ejecuta el scraping y actualización."""
    print(f"Iniciando búsqueda de tickers a las {datetime.datetime.now().strftime('%H:%M:%S')}...")
    conn = conectar()
    if not conn:
        print("No se pudo conectar a la base. Terminando esta ejecución.")
        return

    driver = configurar_navegador()
    datos_tabla = obtener_tabla_finviz(driver)
    driver.quit()

    for datos in datos_tabla:
        volumen_convertido = convertir_volumen(datos[3])
        valores = (obtener_fecha_actual(), datos[0], datos[1], datos[2], volumen_convertido, datos[4], datos[5], None)
        insertar_datos(conn, "TablaFinviz", valores)

    tickers_sin_noticias = [row[1] for row in leer_datos(conn, "TablaFinviz", "Noticia IS NULL OR Noticia = ''")]
    for ticker in tickers_sin_noticias:
        noticia_en = obtener_noticias(ticker)
        # Manejo seguro de la división para traducción
        if "(" in noticia_en and ")" in noticia_en:  # Verificamos que haya un cierre de paréntesis
            partes = noticia_en.split(" (", 1)  # Dividimos en la primera ocurrencia de " ("
            if len(partes) > 1 and ")" in partes[1]:  # Aseguramos que haya contenido después del paréntesis
                texto_base = partes[0]
                texto_parentesis = "(" + partes[1]
                noticia_es = traducir_texto(texto_base) + " " + texto_parentesis
            else:
                noticia_es = traducir_texto(noticia_en)  # Si falla el formato, traducimos todo
        else:
            noticia_es = traducir_texto(noticia_en)  # Si no hay paréntesis, traducimos todo
        actualizar_datos(conn, "TablaFinviz", "Noticia", noticia_es, f"Ticker = '{ticker}'")

    tickers_sin_datos = [row[1] for row in leer_datos(conn, "TablaFinviz", "ShsFloat IS NULL OR ShortFloat IS NULL OR ShortRatio IS NULL OR AvgVolume IS NULL OR CashSh IS NULL")]
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
    print("Búsqueda completada.")

if __name__ == "__main__":
    buscar_tickers()  # Ejecución manual