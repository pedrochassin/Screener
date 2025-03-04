import pyodbc
import configparser

def conectar():
    config = configparser.ConfigParser()
    config.read('../config.ini')  # Sube un nivel desde Código(src)
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

def leer_datos(conexion, tabla):
    try:
        cursor = conexion.cursor()
        cursor.execute(f"SELECT * FROM {tabla}")
        filas = cursor.fetchall()
        cursor.close()
        return filas
    except Exception as e:
        print(f"Error al leer datos de {tabla}: {e}")
        return None