import pyodbc
import configparser

def conectar():
    """Conecta a la base de datos usando config.ini y retorna la conexión."""
    config = configparser.ConfigParser()
    config.read('config.ini')

    try:
        driver = config['database'].get('driver')
        server = config['database'].get('server')
        database = config['database'].get('database')
        username = config['database'].get('username')
        password = config['database'].get('password')

        if not all([driver, server, database, username, password]):
            raise ValueError("Faltan parámetros en el archivo config.ini")

        conexion = pyodbc.connect(
            f"DRIVER={driver};"
            f"SERVER={server};"
            f"DATABASE={database};"
            f"UID={username};"
            f"PWD={password}"
        )
        print("¡Conectado a la base de datos!")
        return conexion
    except Exception as e:
        print(f"No pude conectar... el problema fue: {e}")
        return None

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
import pyodbc
import configparser

def conectar():
    """Conecta a la base de datos usando config.ini y retorna la conexión."""
    config = configparser.ConfigParser()
    config.read('config.ini')

    try:
        driver = config['database'].get('driver')
        server = config['database'].get('server')
        database = config['database'].get('database')
        username = config['database'].get('username')
        password = config['database'].get('password')

        if not all([driver, server, database, username, password]):
            raise ValueError("Faltan parámetros en el archivo config.ini")

        conexion = pyodbc.connect(
            f"DRIVER={driver};"
            f"SERVER={server};"
            f"DATABASE={database};"
            f"UID={username};"
            f"PWD={password}"
        )
        print("¡Conectado a la base de datos!")
        return conexion
    except Exception as e:
        print(f"No pude conectar... el problema fue: {e}")
        return None

def leer_datos(conexion, tabla, condicion=None):
    """Lee datos de una tabla con una condición opcional y retorna las filas."""
    try:
        cursor = conexion.cursor()
        query = f"SELECT * FROM {tabla}" if not condicion else f"SELECT * FROM {tabla} WHERE {condicion}"
        cursor.execute(query)
        filas = cursor.fetchall()
        cursor.close()
        return filas
    except Exception as e:
        print(f"Error al leer datos de {tabla}: {e}")
        return None

def insertar_datos(conexion, tabla, valores):
    """Inserta una fila de datos en la tabla especificada."""
    try:
        cursor = conexion.cursor()
        query = f"INSERT INTO {tabla} (Fecha, Ticker, Precio, CambioPorcentaje, Volumen, Vacío, Categoria, Noticia) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
        cursor.execute(query, valores)
        conexion.commit()
        cursor.close()
    except Exception as e:
        print(f"Error al insertar en {tabla}: {e}")

def actualizar_datos(conexion, tabla, columna, valor, condicion):
    """Actualiza una columna en la tabla según una condición."""
    try:
        cursor = conexion.cursor()
        query = f"UPDATE {tabla} SET {columna} = ? WHERE {condicion}"
        cursor.execute(query, (valor,))
        conexion.commit()
        cursor.close()
    except Exception as e:
        print(f"Error al actualizar {tabla}: {e}")

def actualizar_multiples(conexion, tabla, valores, condicion):
    """Actualiza múltiples columnas en la tabla según una condición."""
    try:
        cursor = conexion.cursor()
        query = f"UPDATE {tabla} SET ShsFloat = COALESCE(ShsFloat, ?), ShortFloat = COALESCE(ShortFloat, ?), ShortRatio = COALESCE(ShortRatio, ?), AvgVolume = COALESCE(AvgVolume, ?), CashSh = COALESCE(CashSh, ?) WHERE {condicion}"
        cursor.execute(query, valores)
        conexion.commit()
        cursor.close()
    except Exception as e:
        print(f"Error al actualizar múltiples en {tabla}: {e}")

def eliminar_datos(conexion, tabla, tickers):
    """Elimina filas de la tabla basadas en una lista de tickers."""
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

# Nueva función para ejecutar procedimientos almacenados
def ejecutar_procedimiento(conexion, nombre_procedimiento):
    """Ejecuta un procedimiento almacenado en la base de datos."""
    try:
        cursor = conexion.cursor()
        cursor.execute(f"EXEC {nombre_procedimiento}")
        conexion.commit()
        print(f"[DEBUG] Procedimiento {nombre_procedimiento} ejecutado con éxito")
    except Exception as e:
        print(f"[DEBUG] Error al ejecutar {nombre_procedimiento}: {e}")
        raise
    finally:
        cursor.close()