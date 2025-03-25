import pyodbc

# Parámetros de conexión directos para evitar posibles errores en config.ini
server = 'localhost,1433'  # O el nombre de tu servidor
database = 'FinvizData'
username = 'sa'
password = '1593Satriani'

try:
    conexion = pyodbc.connect(
        f"DRIVER=ODBC Driver 18 for SQL Server;"
        f"SERVER={server};"
        f"DATABASE={database};"
        f"UID={username};"
        f"PWD={password};"
        "TrustServerCertificate=yes"
    )
    print("✅ ¡Conexión exitosa a la base de datos!")
except Exception as e:
    print(f"❌ Error de conexión: {e}")
