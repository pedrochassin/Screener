from Base_Datos import conectar, leer_datos, insertar_datos, actualizar_datos, actualizar_multiples
from scraper import configurar_navegador, obtener_tabla_finviz, obtener_noticias, obtener_datos_adicionales
from utils import convertir_volumen, traducir_texto, obtener_fecha_actual
import datetime

def buscar_tickers():
    print(f"Iniciando búsqueda de tickers a las {datetime.datetime.now().strftime('%H:%M:%S')}...")
    conn = conectar()
    if not conn:
        print("No se pudo conectar a la base. Terminando esta ejecución.")
        return

    driver = configurar_navegador()
    datos_tabla = obtener_tabla_finviz(driver)
    driver.quit()

    fecha_actual = obtener_fecha_actual()
    print(f"Fecha actual usada: {fecha_actual}")

    print(f"Insertando {len(datos_tabla)} nuevos tickers...")
    for datos in datos_tabla:
        volumen_convertido = convertir_volumen(datos[3])
        valores = (fecha_actual, datos[0], datos[1], datos[2], volumen_convertido, datos[4], datos[5], None)
        try:
            insertar_datos(conn, "TablaFinviz", valores)
        except Exception as e:
            print(f"Error al insertar en TablaFinviz: {e}")

    total_con_fecha = len(leer_datos(conn, "TablaFinviz", f"Fecha = '{fecha_actual}'") or [])
    print(f"Total de registros con Fecha = {fecha_actual} después de inserción: {total_con_fecha}")

    # Actualizar noticias con paréntesis explícitos
    tickers_sin_noticias = [row[1] for row in leer_datos(conn, "TablaFinviz", f"(Noticia IS NULL OR Noticia = '') AND Fecha = '{fecha_actual}'") or []]
    print(f"Actualizando noticias para {len(tickers_sin_noticias)} tickers con Fecha = {fecha_actual}")
    for ticker in tickers_sin_noticias:
        noticia_en = obtener_noticias(ticker)
        if "(" in noticia_en and ")" in noticia_en:
            partes = noticia_en.split(" (", 1)
            if len(partes) > 1 and ")" in partes[1]:
                texto_base = partes[0]
                texto_parentesis = "(" + partes[1]
                noticia_es = traducir_texto(texto_base) + " " + texto_parentesis
            else:
                noticia_es = traducir_texto(noticia_en)
        else:
            noticia_es = traducir_texto(noticia_en)
        actualizar_datos(conn, "TablaFinviz", "Noticia", noticia_es, f"Ticker = '{ticker}'")

    # Actualizar datos adicionales con paréntesis explícitos
    tickers_sin_datos = [row[1] for row in leer_datos(conn, "TablaFinviz", f"(ShsFloat IS NULL OR ShortFloat IS NULL OR ShortRatio IS NULL OR AvgVolume IS NULL OR CashSh IS NULL) AND Fecha = '{fecha_actual}'") or []]
    print(f"Actualizando datos adicionales para {len(tickers_sin_datos)} tickers con Fecha = {fecha_actual}")
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
    buscar_tickers()