import pyodbc
import configparser

def conectar():
    """Conecta a la base de datos usando config.ini."""
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
    """Lee datos de una tabla con una condición opcional."""
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
    """Inserta datos en una tabla."""
    try:
        cursor = conexion.cursor()
        query = f"INSERT INTO {tabla} (Fecha, Ticker, Precio, CambioPorcentaje, Volumen, Vacío, Categoria, Noticia) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
        cursor.execute(query, valores)
        conexion.commit()
        cursor.close()
    except Exception as e:
        print(f"Error al insertar en {tabla}: {e}")

def actualizar_datos(conexion, tabla, columna, valor, condicion):
    """Actualiza una columna en una tabla basado en una condición."""
    try:
        cursor = conexion.cursor()
        query = f"UPDATE {tabla} SET {columna} = ? WHERE {condicion}"
        cursor.execute(query, (valor,))
        conexion.commit()
        cursor.close()
    except Exception as e:
        print(f"Error al actualizar {tabla}: {e}")

def actualizar_multiples(conexion, tabla, valores, condicion):
    """Actualiza múltiples columnas en una tabla."""
    try:
        cursor = conexion.cursor()
        query = f"UPDATE {tabla} SET ShsFloat = COALESCE(ShsFloat, ?), ShortFloat = COALESCE(ShortFloat, ?), ShortRatio = COALESCE(ShortRatio, ?), AvgVolume = COALESCE(AvgVolume, ?), CashSh = COALESCE(CashSh, ?) WHERE {condicion}"
        cursor.execute(query, valores)
        conexion.commit()
        cursor.close()
    except Exception as e:
        print(f"Error al actualizar múltiples en {tabla}: {e}")