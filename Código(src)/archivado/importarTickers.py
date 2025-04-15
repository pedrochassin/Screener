import pandas as pd
import pymssql
import configparser
import numpy as np

# Leer configuración de la base de datos
config = configparser.ConfigParser()
config.read("config.ini")

server = config["database"]["server"]
database = config["database"]["database"]
username = config["database"]["username"]
password = config["database"]["password"]

# Conectar a SQL Server
conn = pymssql.connect(server=server, user=username, password=password, database=database)
cursor = conn.cursor()

# Leer datos desde Excel, forzando Volumen como texto
archivo_excel = "C:\\Users\\Admin\\Documents\\Screener 2025\\Lista de tickers sql.xlsx"
df = pd.read_excel(archivo_excel, sheet_name="Hoja1", usecols=["Fecha", "Ticker", "CambioPorcentaje", "Return", "Open", "Close", "High", "Low", "Volumen"], dtype={"Volumen": str})

# Convertir NaN a None
df = df.replace({pd.NA: None, pd.NaT: None, float('nan'): None})

# Convertir 'CambioPorcentaje' a cadena
df["CambioPorcentaje"] = df["CambioPorcentaje"].astype(str)

# Asegurarse de que Volumen mantenga el formato con comas (si ya está como texto en el Excel, no necesita más cambios)
df["Volumen"] = df["Volumen"].str.replace(',', '', regex=False).apply(lambda x: f"{int(float(x)):,.0f}" if pd.notna(x) else None)

# Redondear valores numéricos y verificar límites
df["Return"] = df["Return"].clip(upper=99999999.99).round(2)
df["Open"] = df["Open"].clip(upper=99999999.99).round(2)
df["Close"] = df["Close"].clip(upper=99999999.99).round(2)
df["High"] = df["High"].clip(upper=99999999.99).round(2)
df["Low"] = df["Low"].clip(upper=99999999.99).round(2)

# Convertir 'Fecha' al formato correcto
df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce").dt.strftime("%Y-%m-%d")

# Verificar si hay datos válidos
if df.empty:
    print("El archivo de Excel está vacío o las columnas requeridas no existen.")
else:
    # Imprimir los valores máximos para depuración
    print("Máximos por columna:", df[["Return", "Open", "Close", "High", "Low"]].max())
    
    # Convertir DataFrame a lista de tuplas, manejando nulos
    datos = [tuple(None if pd.isna(x) else x for x in row) for row in df.itertuples(index=False)]
    print(f"Datos a insertar (primeras 5 filas): {datos[:5]}")

    # Query de inserción con la columna Volumen
    query = """
    INSERT INTO TablaFinviz (Fecha, Ticker, CambioPorcentaje, [Return], [Open], [Close], High, Low, Volumen) 
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    try:
        cursor.executemany(query, datos)
        conn.commit()
        print(f"Se insertaron {len(datos)} registros correctamente.")
    except Exception as e:
        print("Error al insertar datos:", e)
        conn.rollback()
    finally:
        cursor.close()
        conn.close()