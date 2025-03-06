from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit
from PyQt5.QtCore import Qt, QSettings
from gui.utils import show_news

class Sidebar(QWidget):
    """Panel lateral con botones para acciones de la interfaz."""
    def __init__(self, parent):
        """Inicializa la barra lateral con botones."""
        super().__init__(parent)
        self.setStyleSheet("background-color: #191a24;")
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)

        title = QPushButton("Screener 2025")  # Título de la barra lateral
        title.setStyleSheet("font-size: 16px; font-weight: bold; border: none;")
        title.setEnabled(False)  # No clickable
        layout.addWidget(title)

        update_btn = QPushButton("🔄 Actualizar")  # Botón para actualizar datos
        update_btn.clicked.connect(parent.actualizar_datos)
        layout.addWidget(update_btn)

        filter_btn = QPushButton("🔍 Filtrar")  # Botón para abrir ventana de filtros
        filter_btn.clicked.connect(parent.abrir_filtros)
        layout.addWidget(filter_btn)

        news_btn = QPushButton("ℹ️ Ver Noticia")  # Botón para mostrar noticia seleccionada
        news_btn.clicked.connect(lambda: show_news(parent.table))
        layout.addWidget(news_btn)

        delete_btn = QPushButton("🗑️ Eliminar")  # Botón para eliminar filas seleccionadas
        delete_btn.clicked.connect(parent.eliminar_seleccion)
        layout.addWidget(delete_btn)

class DataTable(QTableWidget):
    """Tabla de datos con funcionalidades de ordenamiento y filtrado."""
    def __init__(self, parent):
        """Inicializa la tabla con columnas y configuraciones."""
        super().__init__(parent)
        self.setColumnCount(7)
        self.setHorizontalHeaderLabels(["Fecha", "Ticker", "Precio", "Cambio %", "Volumen", "Categoría", "Noticia"])
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)  # Permite ajustar columnas
        self.horizontalHeader().setMinimumSectionSize(50)
        self.setStyleSheet("""
            QTableWidget {
                background-color: #191a24;
                color: #ffffff;
                selection-background-color: #4a4a4a;
            }
            QHeaderView::section {
                background-color: #191a24;
                color: #ffffff;
                padding: 5px;
                border: 1px solid #3a3a3a;
            }
        """)
        self.setEditTriggers(QTableWidget.NoEditTriggers)  # No editable
        self.horizontalHeader().sectionClicked.connect(self.ordenar_columna)  # Conecta clic a ordenamiento
        self.verticalHeader().setStyleSheet("background-color: #2a2a2a; color: #ffffff;")
        self.sort_orders = {}  # Diccionario para rastrear el orden por columna

        self.filter_input = QLineEdit(self)  # Campo de filtro en tiempo real
        self.filter_input.setPlaceholderText("Filtrar por Ticker...")
        self.filter_input.setStyleSheet("background-color: #3a3a3a; color: #ffffff; padding: 5px;")
        self.filter_input.textChanged.connect(self.filtrar_en_tiempo_real)
        self.filter_input.setMaximumWidth(200)
        self.filter_input.move(10, 10)

        self.settings = QSettings("Screener2025", "TableSettings")  # Configuración para guardar tamaños
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