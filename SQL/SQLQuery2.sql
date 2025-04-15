DELETE FROM TablaFinviz
WHERE Fecha IN (
    SELECT TOP 5435 Fecha
    FROM TablaFinviz
    ORDER BY Fecha DESC
);
