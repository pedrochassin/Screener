import pyodbc
import configparser

def limpiar_bigint(valor):
    """
    Convierte un valor a un número entero válido para la base de datos.
    Si el valor no es válido (como "N/A", "-", o una cadena vacía), devuelve 0.
    """
    if valor is None or str(valor).strip() in ("", "N/A", "-", "null"):
        return 0  # Si no hay valor o es algo como "N/A", devolvemos 0
    try:
        # Elimina comas, espacios y otros caracteres que no son números
        valor_limpio = str(valor).replace(",", "").replace(" ", "")
        return int(valor_limpio)  # Convierte el valor a un número entero
    except (ValueError, TypeError):
        print(f"No se pudo convertir '{valor}' a número, usando 0 como valor por defecto")
        return 0  # Si falla la conversión, devolvemos 0

def conectar():
    """
    Conecta a la base de datos usando un archivo config.ini y devuelve la conexión.
    Necesitas tener un archivo config.ini con los datos de tu base de datos.
    """
    # Lee el archivo de configuración donde están los datos de la base de datos
    config = configparser.ConfigParser()
    config.read('../config.ini')  # Asegúrate de que el archivo config.ini esté en la carpeta correcta

    try:
        # Intenta conectar a la base de datos usando los datos del archivo config.ini
        conexion = pyodbc.connect(
            f"DRIVER={config['database']['driver']};"
            f"SERVER={config['database']['server']};"
            f"DATABASE={config['database']['database']};"
            f"UID={config['database']['username']};"
            f"PWD={config['database']['password']}"
        )
        print("¡Conectado a la base de datos!")
        return conexion
    except Exception as e:
        print(f"No pude conectar... el problema fue: {e}")
        return None

def leer_datos(conexion, tabla, condicion=None):
    """
    Lee datos de una tabla. Si le das una condición, solo lee los datos que cumplen esa condición.
    Devuelve las filas encontradas.
    """
    try:
        cursor = conexion.cursor()
        # Si no hay condición, lee todo; si hay condición, filtra los datos
        query = f"SELECT * FROM {tabla}" if not condicion else f"SELECT * FROM {tabla} WHERE {condicion}"
        cursor.execute(query)
        filas = cursor.fetchall()
        cursor.close()
        return filas
    except Exception as e:
        print(f"Error al leer datos de {tabla}: {e}")
        return None

def insertar_datos(conexion, tabla, valores):
    """
    Inserta una fila nueva en la tabla.
    Los valores deben estar en el orden: Fecha, Ticker, Precio, CambioPorcentaje, Volumen, Vacío, Categoria, Noticia.
    """
    try:
        cursor = conexion.cursor()
        query = f"INSERT INTO {tabla} (Fecha, Ticker, Precio, CambioPorcentaje, Volumen, Vacío, Categoria, Noticia) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
        cursor.execute(query, valores)
        conexion.commit()
        cursor.close()
        print(f"Datos insertados correctamente en {tabla}")
    except Exception as e:
        print(f"Error al insertar en {tabla}: {e}")

def actualizar_datos(conexion, tabla, columna, valor, condicion):
    """
    Actualiza una columna específica en la tabla para las filas que cumplen con la condición.
    """
    try:
        cursor = conexion.cursor()
        query = f"UPDATE {tabla} SET {columna} = ? WHERE {condicion}"
        cursor.execute(query, (valor,))
        conexion.commit()
        cursor.close()
        print(f"Columna {columna} actualizada correctamente en {tabla}")
    except Exception as e:
        print(f"Error al actualizar {tabla}: {e}")

def actualizar_multiples(conexion, tabla, valores, condicion):
    """
    Actualiza varias columnas al mismo tiempo para las filas que cumplen con la condición.
    Los valores deben estar en el orden: ShsFloat, ShortFloat, ShortRatio, AvgVolume, CashSh.
    """
    try:
        # Descompone los valores para validarlos
        shs_float, short_float, short_ratio, avg_volume, cash_sh = valores
        
        # Limpia y valida el valor para AvgVolume (que debe ser un número grande)
        avg_volume_limpio = limpiar_bigint(avg_volume)
        
        # Reconstruye los valores con el dato limpio
        valores_limpios = (shs_float, short_float, short_ratio, avg_volume_limpio, cash_sh)
        
        # Imprime los valores para depurar
        print(f"Valores limpios antes de actualizar: {valores_limpios}")
        
        cursor = conexion.cursor()
        query = f"UPDATE {tabla} SET ShsFloat = COALESCE(ShsFloat, ?), ShortFloat = COALESCE(ShortFloat, ?), ShortRatio = COALESCE(ShortRatio, ?), AvgVolume = COALESCE(AvgVolume, ?), CashSh = COALESCE(CashSh, ?) WHERE {condicion}"
        cursor.execute(query, valores_limpios)
        conexion.commit()
        cursor.close()
        print(f"Columnas actualizadas correctamente en {tabla}")
    except Exception as e:
        print(f"Error al actualizar múltiples en {tabla}: {e}")

def eliminar_datos(conexion, tabla, tickers):
    """
    Elimina filas de la tabla basadas en una lista de tickers.
    """
    try:
        cursor = conexion.cursor()
        placeholders = ','.join('?' * len(tickers))
        query = f"DELETE FROM {tabla} WHERE Ticker IN ({placeholders})"
        cursor.execute(query, tickers)
        conexion.commit()
        cursor.close()
        print(f"Eliminados {len(tickers)} tickers de {tabla}")
    except Exception as e:
        print(f"Error al eliminar datos de {tabla}: {e}")

# Ejemplo de cómo usar este código (puedes eliminar esta parte si no la necesitas)
if __name__ == "__main__":
    # Intenta conectar a la base de datos
    conexion = conectar()
    if conexion:
        # Ejemplo: Leer datos de la tabla
        datos = leer_datos(conexion, "TablaFinviz")
        if datos:
            print(f"Se encontraron {len(datos)} filas en TablaFinviz")

        # Ejemplo: Insertar datos
        valores_insertar = ("2023-10-03", "AAPL", 150.25, "2.5%", "1000000", "", "Tecnología", "Ninguna noticia")
        insertar_datos(conexion, "TablaFinviz", valores_insertar)

        # Ejemplo: Actualizar múltiples columnas
        valores_actualizar = ("10M", "5%", "2.5", "1000000", "50M")
        actualizar_multiples(conexion, "TablaFinviz", valores_actualizar, "Ticker = 'AAPL'")

        # Ejemplo: Eliminar datos
        tickers_a_eliminar = ["AAPL", "GOOGL"]
        eliminar_datos(conexion, "TablaFinviz", tickers_a_eliminar)

        # Cierra la conexión cuando termines
        conexion.close()