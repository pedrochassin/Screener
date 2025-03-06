import pyodbc
import configparser

def conectar():
    """Conecta a la base de datos usando config.ini y retorna la conexión."""
    config = configparser.ConfigParser()
    config.read('../config.ini')

    try:
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
        # Crea una consulta con múltiples condiciones IN para los tickers
        placeholders = ','.join('?' * len(tickers))
        query = f"DELETE FROM {tabla} WHERE Ticker IN ({placeholders})"
        cursor.execute(query, tickers)
        conexion.commit()
        cursor.close()
        print(f"Eliminados {len(tickers)} tickers de {tabla}")
    except Exception as e:
        print(f"Error al eliminar datos de {tabla}: {e}")