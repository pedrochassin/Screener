from Base_Datos import conectar as conectar

def leer_datos(conexion, tabla):
    cursor = conexion.cursor()
    cursor.execute(f"SELECT * FROM {tabla}")
    return cursor.fetchall()

# Elige la tabla que quieres leer
tabla_a_leer = "TablaFinviz"  # Cambia esto por cualquier tabla

print("¡Hola desde mi proyecto!")
conexion = conectar()
if conexion:
    datos = leer_datos(conexion, tabla_a_leer)
    if datos:
        print(f"Datos de {tabla_a_leer}:")
        for fila in datos:
            print(fila)
    else:
        print(f"No pude leer datos de {tabla_a_leer}...")
    conexion.close()
else:
    print("No hay conexión, no puedo hacer nada.")