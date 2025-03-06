from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit, QMenu, QApplication, QAction
from PyQt5.QtCore import Qt, QSettings, QMimeData

class Sidebar(QWidget):
    """Panel lateral vacío (sin título ni botones)."""
    def __init__(self, parent):
        """Inicializa la barra lateral sin elementos."""
        super().__init__(parent)
        self.setStyleSheet("background-color: #2a2a2a;")
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)

class DataTable(QTableWidget):
    """Tabla de datos con funcionalidades de ordenamiento, filtrado y menú contextual."""
    def __init__(self, parent):
        """Inicializa la tabla con columnas y configuraciones."""
        super().__init__(parent)
        self.app = parent  # Guardamos referencia a ScreenerApp
        self.setColumnCount(7)
        self.setHorizontalHeaderLabels(["Fecha", "Ticker", "Precio", "Cambio %", "Volumen", "Categoría", "Noticia"])
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.horizontalHeader().setMinimumSectionSize(50)
        self.setStyleSheet("""
            QTableWidget {
                background-color: #2a2a2a;
                color: #ffffff;
                selection-background-color: #4a4a4a;
            }
            QHeaderView::section {
                background-color: #2a2a2a;
                color: #ffffff;
                padding: 5px;
                border: 1px solid #3a3a3a;
            }
        """)
        self.setEditTriggers(QTableWidget.NoEditTriggers)
        self.horizontalHeader().sectionClicked.connect(self.ordenar_columna)
        self.verticalHeader().setStyleSheet("background-color: #2a2a2a; color: #ffffff;")
        self.sort_orders = {}
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.mostrar_menu_contextual)

        self.filter_input = QLineEdit(self)
        self.filter_input.setPlaceholderText("Filtrar por Ticker...")
        self.filter_input.setStyleSheet("background-color: #3a3a3a; color: #ffffff; padding: 5px;")
        self.filter_input.textChanged.connect(self.filtrar_en_tiempo_real)
        self.filter_input.setMaximumWidth(200)
        self.filter_input.move(10, 10)

        self.settings = QSettings("Screener2025", "TableSettings")
        self.cargar_tamanos()

    def cargar_datos(self, datos):
        """Carga datos en la tabla desde la base de datos."""
        self.datos_completos = datos
        self.setRowCount(0)
        for fila in datos:
            row = self.rowCount()
            self.insertRow(row)
            for col, value in enumerate([fila[0], fila[1], fila[2], fila[3], fila[4], fila[6], fila[7]]):
                self.setItem(row, col, QTableWidgetItem(str(value)))
        self.cargar_tamanos()

    def filtrar_en_tiempo_real(self, texto):
        """Filtra filas en tiempo real según el texto ingresado en el campo de filtro."""
        self.setRowCount(0)
        for fila in self.datos_completos:
            if texto.lower() in str(fila[1]).lower():
                row = self.rowCount()
                self.insertRow(row)
                for col, value in enumerate([fila[0], fila[1], fila[2], fila[3], fila[4], fila[6], fila[7]]):
                    self.setItem(row, col, QTableWidgetItem(str(value)))
        self.cargar_tamanos()

    def ordenar_columna(self, column):
        """Ordena la columna clicada, alternando entre descendente y ascendente."""
        if column not in self.sort_orders:
            self.sort_orders[column] = Qt.DescendingOrder
        else:
            self.sort_orders[column] = Qt.AscendingOrder if self.sort_orders[column] == Qt.DescendingOrder else Qt.DescendingOrder
        self.sortItems(column, self.sort_orders[column])
        self.horizontalHeader().setSortIndicator(column, self.sort_orders[column])

    def cargar_tamanos(self):
        """Carga los tamaños de columna guardados desde QSettings."""
        for col in range(self.columnCount()):
            width = self.settings.value(f"column_{col}", 100, type=int)
            self.setColumnWidth(col, width)

    def guardar_tamanos(self):
        """Guarda los tamaños de columna en QSettings al cerrar."""
        for col in range(self.columnCount()):
            self.settings.setValue(f"column_{col}", self.columnWidth(col))

    def closeEvent(self, event):
        """Evento que se ejecuta al cerrar la tabla, guarda los tamaños."""
        self.guardar_tamanos()
        super().closeEvent(event)

    def mostrar_menu_contextual(self, pos):
        """Muestra un menú contextual al hacer clic derecho sobre la tabla."""
        from gui.utils import show_news
        menu = QMenu(self)
        news_action = QAction("ℹ️ Ver Noticia", self)
        news_action.triggered.connect(lambda: show_news(self))
        menu.addAction(news_action)

        delete_action = QAction("🗑️ Eliminar", self)
        delete_action.triggered.connect(lambda: self.app.eliminar_seleccion())  # Usamos self.app en lugar de self.parent()
        menu.addAction(delete_action)

        copy_action = QAction("📋 Copiar", self)
        copy_action.triggered.connect(self.copiar_seleccion)
        menu.addAction(copy_action)

        menu.exec_(self.mapToGlobal(pos))

    def copiar_seleccion(self):
        """Copia solo las celdas seleccionadas al portapapeles."""
        selected = self.selectedItems()
        if not selected:
            return

        text = ""
        for item in selected:
            text += item.text() + "\t"
        text = text.strip()

        clipboard = QApplication.clipboard()
        clipboard.setText(text)

    def eliminar_seleccion(self):
        """Redirige la eliminación al método del padre (no usado directamente aquí)."""
        self.app.eliminar_seleccion()  # Usamos self.app