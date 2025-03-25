from PyQt5.QtWidgets import QStyledItemDelegate, QTableWidgetItem, QStyle  # Movemos QStyle aquí
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QColor, QPainter, QBrush, QFont
from datetime import datetime

# Clase para personalizar la apariencia de las celdas con esquinas redondeadas (condicional a la fecha)
class RoundedRectDelegate(QStyledItemDelegate):
    def __init__(self, parent=None, date_column=0, rounded_columns=None, text_color="#00f4cf", background_color="#0e2524"):
        super().__init__(parent)
        self.date_column = date_column  # Columna que contiene la fecha
        self.rounded_columns = rounded_columns if rounded_columns is not None else []  # Columnas con redondeado
        self.text_color = QColor(text_color)  # Color del texto personalizable
        self.background_color = QColor(background_color)  # Color de fondo personalizable

    # Método para personalizar la pintura de las celdas
    def paint(self, painter, option, index):
        # Verifica si la celda está seleccionada
        is_selected = option.state & QStyle.State_Selected

        # Verifica si la columna actual está en las columnas con redondeado
        if index.column() in self.rounded_columns:
            table = self.parent()  # Obtiene la tabla asociada
            date_item = table.item(index.row(), self.date_column)  # Obtiene el ítem de la columna de fecha
            hoy = datetime.now().strftime("%Y-%m-%d")  # Obtiene la fecha actual en formato "YYYY-MM-DD"
            if date_item and date_item.text() == hoy:  # Verifica si la fecha coincide con la actual
                painter.save()  # Guarda el estado actual del pintor

                radius = 10  # Radio de las esquinas redondeadas

                # Dibujar el fondo de selección si la celda está seleccionada
                if is_selected:
                    painter.setRenderHint(QPainter.Antialiasing)
                    selection_brush = QBrush(option.palette.highlight().color())  # Color de resaltado de selección
                    painter.setBrush(selection_brush)
                    painter.setPen(Qt.NoPen)
                    rect = QRect(option.rect.adjusted(2, 2, -2, -2))
                    painter.drawRoundedRect(rect, radius, radius)

                # Dibujar el fondo redondeado personalizado
                painter.setRenderHint(QPainter.Antialiasing)  # Habilita el suavizado de bordes
                brush = QBrush(self.background_color)  # Crea un pincel con el color de fondo
                painter.setBrush(brush)  # Aplica el pincel al pintor
                painter.setPen(Qt.NoPen)  # Elimina el borde de la celda
                rect = QRect(option.rect.adjusted(2, 2, -2, -2))
                painter.drawRoundedRect(rect, radius, radius)

                painter.restore()  # Restaura el estado del pintor

                painter.save()  # Guarda el estado nuevamente para pintar el texto
                # Preservar la fuente existente del ítem
                item = table.item(index.row(), index.column())
                if item and item.font():
                    painter.setFont(item.font())  # Usa la fuente del ítem (incluye negrita si está configurada)
                # Usar color de texto resaltado si está seleccionado, o el personalizado si no
                text_color = option.palette.highlightedText().color() if is_selected else self.text_color
                painter.setPen(text_color)  # Aplica el color del texto
                text = index.data(Qt.DisplayRole) if index.data(Qt.DisplayRole) is not None else ""  # Obtiene el texto de la celda
                painter.drawText(option.rect, Qt.AlignCenter, text)  # Dibuja el texto centrado
                painter.restore()  # Restaura el estado del pintor
                return  # Finaliza la personalización de la celda

        # Si no es una celda con redondeado o no cumple la condición, usa la pintura predeterminada
        super().paint(painter, option, index)

# Clase para redondeados independientes con estilos por columna
class CustomRoundedDelegate(QStyledItemDelegate):
    def __init__(self, parent=None, rounded_styles=None):
        super().__init__(parent)
        self.rounded_styles = rounded_styles if rounded_styles is not None else {}  # Diccionario de estilos por columna

    # Método para personalizar la pintura de las celdas con redondeado independiente
    def paint(self, painter, option, index):
        # Verifica si la celda está seleccionada
        is_selected = option.state & QStyle.State_Selected

        if index.column() in self.rounded_styles:  # Verifica si la columna tiene un estilo redondeado
            style = self.rounded_styles[index.column()]  # Obtiene el estilo específico de la columna
            painter.save()  # Guarda el estado actual del pintor

            radius = 10  # Radio de las esquinas redondeadas

            # Dibujar el fondo de selección si la celda está seleccionada
            if is_selected:
                painter.setRenderHint(QPainter.Antialiasing)
                selection_brush = QBrush(option.palette.highlight().color())  # Color de resaltado de selección
                painter.setBrush(selection_brush)
                painter.setPen(Qt.NoPen)
                rect = QRect(option.rect.adjusted(2, 2, -2, -2))
                painter.drawRoundedRect(rect, radius, radius)

            # Dibujar el fondo redondeado personalizado
            painter.setRenderHint(QPainter.Antialiasing)  # Habilita el suavizado de bordes
            brush = QBrush(QColor(style.get('background_color', '#ffffff')))  # Color de fondo, blanco por defecto
            painter.setBrush(brush)  # Aplica el pincel al pintor
            painter.setPen(Qt.NoPen)  # Elimina el borde de la celda
            rect = QRect(option.rect.adjusted(2, 2, -2, -2))
            painter.drawRoundedRect(rect, radius, radius)

            painter.restore()  # Restaura el estado del pintor

            painter.save()  # Guarda el estado nuevamente para pintar el texto
            table = self.parent()
            # Preservar la fuente existente del ítem
            item = table.item(index.row(), index.column())
            if item and item.font():
                painter.setFont(item.font())  # Usa la fuente del ítem (incluye negrita si está configurada)
            # Usar color de texto resaltado si está seleccionado, o el personalizado si no
            text_color = option.palette.highlightedText().color() if is_selected else QColor(style.get('text_color', '#000000'))
            painter.setPen(text_color)  # Aplica el color del texto
            text = index.data(Qt.DisplayRole) if index.data(Qt.DisplayRole) is not None else ""  # Obtiene el texto de la celda
            painter.drawText(option.rect, Qt.AlignCenter, text)  # Dibuja el texto centrado
            painter.restore()  # Restaura el estado del pintor
            return  # Finaliza la personalización de la celda

        # Si no es una celda con redondeado, usa la pintura predeterminada
        super().paint(painter, option, index)

# Función para personalizar la tabla con configuraciones por columna
def customize_table(table, column_styles=None):
    """
    Aplica personalización a la tabla según un diccionario de estilos por columna.
    column_styles: Diccionario donde las claves son índices de columnas y los valores son diccionarios
                   con propiedades como 'align', 'bold', 'color', etc.
    Ejemplo: {1: {'bold': True}, 2: {'align': Qt.AlignCenter, 'color': '#ffffff'}}
    """
    if column_styles is None:
        column_styles = {}  # Diccionario vacío si no se proporciona configuración

    for row in range(table.rowCount()):  # Itera sobre las filas de la tabla
        for col in range(table.columnCount()):  # Itera sobre todas las columnas
            if col in column_styles:  # Verifica si la columna tiene una configuración personalizada
                item = table.item(row, col)  # Obtiene el ítem de la celda
                if not item:
                    # Si no hay ítem, crea uno con el texto existente o vacío
                    text = table.item(row, col).text() if table.item(row, col) else ""
                    item = QTableWidgetItem(text)
                    table.setItem(row, col, item)

                # Aplicar estilos según el diccionario de configuración
                style = column_styles[col]
                
                # Alineación
                if 'align' in style:
                    item.setTextAlignment(style['align'])

                # Negrita
                if 'bold' in style and style['bold']:
                    font = item.font()  # Obtiene la fuente del ítem
                    font.setBold(True)  # Configura la fuente como negrita
                    item.setFont(font)  # Aplica la fuente al ítem

                # Color del texto (si se especifica)
                if 'color' in style:
                    item.setForeground(QColor(style['color']))

# Función para aplicar el delegado de celdas redondeadas condicional a la fecha
def apply_delegate(table, date_column=0, rounded_columns=[2, 3, 4, 11, 18, 19], text_color="#00f4cf", background_color="#0e2524"):
    """Aplica el delegado de celdas redondeadas a las columnas especificadas (condicional a la fecha)."""
    delegate = RoundedRectDelegate(table, date_column=date_column, rounded_columns=rounded_columns, 
                                  text_color=text_color, background_color=background_color)  # Crea el delegado
    for col in rounded_columns:  # Itera sobre las columnas con redondeado
        table.setItemDelegateForColumn(col, delegate)  # Aplica el delegado a cada columna

# Función para aplicar redondeados independientes con estilos por columna
def apply_custom_rounded(table, rounded_styles=None):
    """
    Aplica redondeados independientes a columnas con estilos personalizados.
    rounded_styles: Diccionario donde las claves son índices de columnas y los valores son diccionarios
                    con 'background_color' y 'text_color'.
    Ejemplo: {1: {'background_color': '#ff0000', 'text_color': '#ffffff'}}
    """
    if rounded_styles is None:
        rounded_styles = {}  # Diccionario vacío si no se proporciona configuración
    delegate = CustomRoundedDelegate(table, rounded_styles=rounded_styles)  # Crea el delegado
    for col in rounded_styles.keys():  # Itera sobre las columnas con estilos redondeados
        table.setItemDelegateForColumn(col, delegate)  # Aplica el delegado a cada columna