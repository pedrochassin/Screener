from PyQt5.QtCore import Qt
from Base_Datos import conectar, leer_datos, eliminar_datos
from .filters import FilterDialog
from .utils import export_to_csv
from .table_customization import customize_table

def guardar_estado_tabla(app):
    header = app.table.horizontalHeader()
    seleccion = app.table.selectedIndexes()
    app.estado_seleccion = [(index.row(), index.column()) for index in seleccion] if seleccion else []
    app.estado_orden = {
        'columna': header.sortIndicatorSection(),
        'orden': header.sortIndicatorOrder()
    }
    app.estado_posiciones = [header.logicalIndex(i) for i in range(header.count())]
    app.estado_scroll = {
        'vertical': app.table.verticalScrollBar().value(),
        'horizontal': app.table.horizontalScrollBar().value()
    }

def restaurar_estado_tabla(app):
    header = app.table.horizontalHeader()
    if hasattr(app, 'estado_posiciones'):
        for visual_index, logical_index in enumerate(app.estado_posiciones):
            header.moveSection(header.visualIndex(logical_index), visual_index)
    if hasattr(app, 'estado_orden') and app.estado_orden['columna'] is not None:
        app.table.sortItems(app.estado_orden['columna'], app.estado_orden['orden'])
        header.setSortIndicator(app.estado_orden['columna'], app.estado_orden['orden'])
    if hasattr(app, 'estado_seleccion'):
        app.table.clearSelection()
        for row, col in app.estado_seleccion:
            if row < app.table.rowCount() and col < app.table.columnCount():
                app.table.setItemSelected(app.table.item(row, col), True)
    if hasattr(app, 'estado_scroll'):
        app.table.verticalScrollBar().setValue(app.estado_scroll['vertical'])
        app.table.horizontalScrollBar().setValue(app.estado_scroll['horizontal'])

def cargar_datos(app):
    guardar_estado_tabla(app)
    conn = conectar()
    if conn:
        try:
            datos = leer_datos(conn, "TablaFinviz")
            for row in datos:
                if isinstance(row, dict) and 'Noticia' in row and row['Noticia']:
                    row['Noticia'] = row['Noticia'][:255]
                elif isinstance(row, tuple):
                    row = list(row)
                    if len(row) > 5:
                        row[5] = row[5][:255] if row[5] else row[5]
            app.table.cargar_datos(datos)
            restaurar_estado_tabla(app)
            column_styles = {
                1: {'bold': True},
                2: {'align': Qt.AlignCenter},
                3: {'align': Qt.AlignCenter},
                4: {'align': Qt.AlignCenter},
                6: {'bold': True},
                11: {'align': Qt.AlignCenter},
                18: {'align': Qt.AlignCenter},
                19: {'align': Qt.AlignCenter},
                13: {'bold': True, 'align': Qt.AlignCenter, 'color': '#00f4cf'},
            }
            customize_table(app.table, column_styles)
        except Exception as e:
            app.status_bar.showMessage(f"Error al cargar datos: {str(e)}", 10000)
        finally:
            conn.close()

def aplicar_filtro(app, filtros):
    conn = conectar()
    if conn:
        try:
            condiciones = []
            if filtros["ticker"]:
                condiciones.append(f"Ticker LIKE '%{filtros['ticker']}%'")
            if filtros["cambio"]:
                condiciones.append(f"CAST(CambioPorcentaje AS FLOAT) {filtros['cambio_operador']} {filtros['cambio']}")
            if filtros["volumen"]:
                condiciones.append(f"CAST(REPLACE(Volumen, ',', '') AS BIGINT) {filtros['volumen_operador']} {filtros['volumen']}")
            if filtros["categoria"]:
                condiciones.append(f"Categoria LIKE '%{filtros['categoria']}%'")
            query = " AND ".join(condiciones) if condiciones else None
            datos = leer_datos(conn, "TablaFinviz", query)
            app.table.cargar_datos(datos)
        except Exception as e:
            app.status_bar.showMessage(f"Error al aplicar filtro: {str(e)}", 10000)
        finally:
            conn.close()

def exportar_datos(app):
    export_to_csv(app.table)

def actualizar_estado(app):
    selected = app.table.selectedItems()
    if selected:
        cambio = app.table.item(selected[0].row(), 3).text()
        app.status_bar.showMessage(f"Cambio seleccionado: {cambio}")
    else:
        app.status_bar.showMessage("Selecciona una fila para ver el cambio")

def eliminar_seleccion(app):
    selected = app.table.selectedItems()
    if not selected:
        app.status_bar.showMessage("No hay filas seleccionadas para eliminar")
        return
    tickers = {app.table.item(item.row(), 1).text() for item in selected}
    conn = conectar()
    if conn:
        try:
            eliminar_datos(conn, "TablaFinviz", list(tickers))
            cargar_datos(app)
        except Exception as e:
            app.status_bar.showMessage(f"Error al eliminar selección: {str(e)}", 10000)
        finally:
            conn.close()