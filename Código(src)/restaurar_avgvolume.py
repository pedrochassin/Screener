from Base_Datos import conectar

conn = conectar()
if conn:
    try:
        cursor = conn.cursor()
        query = """
        SELECT Ticker, AvgVolume
        FROM [dbo].[TablaFinviz]
        WHERE [AvgVolume] IS NOT NULL
        AND TRY_CAST([AvgVolume] AS BIGINT) IS NULL
        """
        cursor.execute(query)
        print("Valores en AvgVolume que no se pueden convertir a bigint:")
        for row in cursor.fetchall():
            print(row)
        
        # Verificar tipo de dato actual
        cursor.execute("SELECT COLUMN_NAME, DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'TablaFinviz' AND COLUMN_NAME = 'AvgVolume'")
        print("Definición de AvgVolume:", cursor.fetchone())
    except Exception as e:
        print(f"Error: {e}")
    finally:
        cursor.close()
        conn.close()
else:
    print("No se pudo conectar a la base de datos.")