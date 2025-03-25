-- Crear el procedimiento almacenado
CREATE PROCEDURE CalcularRvolYReturn
AS
BEGIN
    SET NOCOUNT ON; -- Evita mensajes innecesarios

    -- Actualizar las columnas Rvol y Return
    UPDATE dbo.TablaFinviz
    SET 
        Rvol = CASE 
                  WHEN TRY_CAST(REPLACE(AvgVolume, ',', '') AS BIGINT) = 0 THEN 0
                  ELSE CAST(TRY_CAST(REPLACE(VolumenActual, ',', '') AS BIGINT) / NULLIF(TRY_CAST(REPLACE(AvgVolume, ',', '') AS BIGINT), 0) AS DECIMAL(10, 2))
               END,
        [Return] = CASE 
                      WHEN [Low] = 0 THEN 0
                      ELSE (High - [Low]) / NULLIF([Low], 0) * 100
                   END;
END;
GO