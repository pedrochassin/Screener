import pyodbc
import configparser

def conectar():
    """Conecta a la base de datos usando config.ini y retorna la conexión."""
    # Crea un objeto ConfigParser para leer el archivo de configuración.
    config = configparser.ConfigParser()
    # Lee el archivo de configuración donde están las credenciales de la base de datos.
    config.read('../config.ini')

    try:
        # Usa pyodbc para crear una conexión con la base de datos usando los parámetros del archivo de configuración.
        conexion = pyodbc.connect(
            f"DRIVER={config['database']['driver']};"
            f"SERVER={config['database']['server']};"
            f"DATABASE={config['database']['database']};"
            f"UID={config['database']['username']};"
            f"PWD={config['database']['password']}"
        )
        print("¡Conectado a la base de datos!")  # Imprime mensaje de éxito.
        return conexion  # Retorna la conexión establecida.
    except Exception as e:
        # Si ocurre un error al conectar, imprime el mensaje de error.
        print(f"No pude conectar... el problema fue: {e}")
        return None  # Si no se puede conectar, retorna None.

def leer_datos(conexion, tabla, condicion=None):
    """Lee datos de una tabla con una condición opcional y retorna las filas."""
    try:
        # Crea un cursor para ejecutar consultas en la base de datos.
        cursor = conexion.cursor()
        # Si no hay condición, selecciona todos los datos de la tabla. Si hay condición, la aplica en la consulta.
        query = f"SELECT * FROM {tabla}" if not condicion else f"SELECT * FROM {tabla} WHERE {condicion}"
        cursor.execute(query)  # Ejecuta la consulta.
        filas = cursor.fetchall()  # Obtiene todas las filas que cumplen con la consulta.
        cursor.close()  # Cierra el cursor.
        return filas  # Retorna las filas obtenidas.
    except Exception as e:
        # Si ocurre un error al leer datos, imprime el mensaje de error.
        print(f"Error al leer datos de {tabla}: {e}")
        return None  # Retorna None en caso de error.

def insertar_datos(conexion, tabla, valores):
    """Inserta una fila de datos en la tabla especificada."""
    try:
        # Crea un cursor para ejecutar la consulta de inserción.
        cursor = conexion.cursor()
        # Define la consulta SQL para insertar los datos.
        query = f"INSERT INTO {tabla} (Fecha, Ticker, Precio, CambioPorcentaje, Volumen, Vacío, Categoria, Noticia) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
        cursor.execute(query, valores)  # Ejecuta la consulta con los valores proporcionados.
        conexion.commit()  # Confirma la transacción en la base de datos.
        cursor.close()  # Cierra el cursor.
    except Exception as e:
        # Si ocurre un error al insertar datos, imprime el mensaje de error.
        print(f"Error al insertar en {tabla}: {e}")

def actualizar_datos(conexion, tabla, columna, valor, condicion):
    """Actualiza una columna en la tabla según una condición."""
    try:
        # Crea un cursor para ejecutar la consulta de actualización.
        cursor = conexion.cursor()
        # Define la consulta SQL para actualizar la columna específica.
        query = f"UPDATE {tabla} SET {columna} = ? WHERE {condicion}"
        cursor.execute(query, (valor,))  # Ejecuta la consulta con el nuevo valor.
        conexion.commit()  # Confirma la transacción.
        cursor.close()  # Cierra el cursor.
    except Exception as e:
        # Si ocurre un error al actualizar, imprime el mensaje de error.
        print(f"Error al actualizar {tabla}: {e}")

def actualizar_multiples(conexion, tabla, valores, condicion):
    """Actualiza múltiples columnas en la tabla según una condición."""
    try:
        # Crea un cursor para ejecutar la consulta de actualización múltiple.
        cursor = conexion.cursor()
        # Define la consulta SQL para actualizar múltiples columnas a la vez.
        query = f"UPDATE {tabla} SET ShsFloat = COALESCE(ShsFloat, ?), ShortFloat = COALESCE(ShortFloat, ?), ShortRatio = COALESCE(ShortRatio, ?), AvgVolume = COALESCE(AvgVolume, ?), CashSh = COALESCE(CashSh, ?) WHERE {condicion}"
        cursor.execute(query, valores)  # Ejecuta la consulta con los valores proporcionados.
        conexion.commit()  # Confirma la transacción.
        cursor.close()  # Cierra el cursor.
    except Exception as e:
        # Si ocurre un error al actualizar múltiples columnas, imprime el mensaje de error.
        print(f"Error al actualizar múltiples en {tabla}: {e}")

def eliminar_datos(conexion, tabla, tickers):
    """Elimina filas de la tabla basadas en una lista de tickers."""
    try:
        # Crea un cursor para ejecutar la consulta de eliminación.
        cursor = conexion.cursor()
        # Crea una consulta con múltiples condiciones IN para los tickers proporcionados.
        placeholders = ','.join('?' * len(tickers))  # Genera un string con placeholders para los tickers.
        query = f"DELETE FROM {tabla} WHERE Ticker IN ({placeholders})"
        cursor.execute(query, tickers)  # Ejecuta la consulta con la lista de tickers.
        conexion.commit()  # Confirma la transacción.
        cursor.close()  # Cierra el cursor.
        print(f"Eliminados {len(tickers)} tickers de {tabla}")  # Imprime el número de tickers eliminados.
    except Exception as e:
        # Si ocurre un error al eliminar los datos, imprime el mensaje de error.
        print(f"Error al eliminar datos de {tabla}: {e}")
