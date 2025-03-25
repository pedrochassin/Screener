from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit, QMenu, QApplication, QAction
from PyQt5.QtCore import Qt, QSettings

class NumericTableWidgetItem(QTableWidgetItem):
    """Subclase de QTableWidgetItem para permitir ordenamiento numérico en la tabla."""
    
    def __lt__(self, other):
        """
        Compara ítems como números si tienen datos en Qt.UserRole.
        
        Args:
            other (QTableWidgetItem): Otro ítem con el que comparar.
        
        Returns:
            bool: True si el valor numérico del ítem actual es menor que el otro.
        """
        if self.data(Qt.UserRole) is not None and other.data(Qt.UserRole) is not None:
            return self.data(Qt.UserRole) < other.data(Qt.UserRole)
        return super().__lt__(other)

class DataTable(QTableWidget):
    """Tabla personalizada para mostrar datos con ordenamiento, filtrado y menú contextual."""
    
    def __init__(self, parent):
        """
        Inicializa la tabla con columnas predefinidas y configuraciones.
        
        Args:
            parent (ScreenerApp): Instancia de la ventana principal de la aplicación.
        """
        super().__init__(parent)
        self.app = parent  # Guardamos referencia a ScreenerApp
        self.setColumnCount(20)  # Número de columnas en la tabla
        self.setHorizontalHeaderLabels([
            "Fecha", "Ticker", "Precio", "Cambio %", "Volumen", "Vacío", "Categoría", "Noticia",
            "ShsFloat", "ShortFloat", "ShortRatio", "AvgVolume", "CashSh", "VolumenActual", "Open", "Close", "High", "Low", "Rvol", "Return" ])  # Encabezados de las columnas
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.horizontalHeader().setMinimumSectionSize(50)
        self.setStyleSheet("""
            QTableWidget {
                background-color: #12131b;
                color: #ffffff;
                selection-background-color: #232533;
            }
            QHeaderView::section {
                background-color: #232533;
                color: #ffffff;
                padding: 5px;
                border: 1px solid #0e0f15;
            }
        """)
        self.setEditTriggers(QTableWidget.NoEditTriggers)  # Desactiva edición directa
        self.horizontalHeader().sectionClicked.connect(self.ordenar_columna)
        self.verticalHeader().setStyleSheet("background-color: #0e0f15; color: #ffffff;")
        self.sort_orders = {}  # Diccionario para almacenar el orden de cada columna
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.mostrar_menu_contextual)

        self.filter_input = QLineEdit(self)
        self.filter_input.setPlaceholderText("Filtrar por Ticker...")
        self.filter_input.setStyleSheet("background-color: #0e0f15; color: #ffffff; padding: 5px;")
        self.filter_input.textChanged.connect(self.filtrar_en_tiempo_real)
        self.filter_input.setMaximumWidth(200)
        self.filter_input.move(10, 10)

        self.settings = QSettings("Screener2025", "TableSettings")
        self.cargar_tamanos()

    def cargar_datos(self, datos):
        """
        Carga datos desde la base de datos en la tabla.
        
        Args:
            datos (list): Lista de filas con datos obtenidos de la base de datos.
        """
        self.datos_completos = datos
        self.setRowCount(0)
        for fila in datos:
            row = self.rowCount()
            self.insertRow(row)
            for col, value in enumerate(fila):
                if col == 13:  # Columna VolumenActual
                    try:
                        # Formatear el valor con separadores de miles
                        formatted_value = "{:,}".format(int(value))
                        item = NumericTableWidgetItem(formatted_value)
                        # Guardamos el valor numérico original para ordenamiento
                        item.setData(Qt.UserRole, float(value))
                    except (ValueError, TypeError):
                        item = NumericTableWidgetItem(str(value) if value is not None else "")
                        item.setData(Qt.UserRole, 0.0)
                elif col in [2, 3, 4, 7, 8, 9, 10, 11, 12, 14, 15, 16, 17, 18, 19]:  # Otras columnas numéricas
                    item = NumericTableWidgetItem(str(value))
                    item.setData(Qt.UserRole, self.parse_number(str(value)))
                else:
                    item = QTableWidgetItem(str(value))
                self.setItem(row, col, item)
        self.cargar_tamanos()

    def filtrar_en_tiempo_real(self, texto):
        """
        Filtra filas en tiempo real según el texto ingresado en el campo de filtro.
        
        Args:
            texto (str): Texto ingresado por el usuario para filtrar por Ticker.
        """
        self.setRowCount(0)
        for fila in self.datos_completos:
            if texto.lower() in str(fila[1]).lower():
                row = self.rowCount()
                self.insertRow(row)
                for col, value in enumerate(fila):
                    if col == 13:  # Columna VolumenActual
                        try:
                            # Formatear el valor con separadores de miles
                            formatted_value = "{:,}".format(int(value))
                            item = NumericTableWidgetItem(formatted_value)
                            # Guardamos el valor numérico original para ordenamiento
                            item.setData(Qt.UserRole, float(value))
                        except (ValueError, TypeError):
                            item = NumericTableWidgetItem(str(value) if value is not None else "")
                            item.setData(Qt.UserRole, 0.0)
                    elif col in [2, 3, 4, 7, 8, 9, 10, 11, 12, 14, 15, 16, 17, 18, 19]:  # Otras columnas numéricas
                        item = NumericTableWidgetItem(str(value))
                        item.setData(Qt.UserRole, self.parse_number(str(value)))
                    else:
                        item = QTableWidgetItem(str(value))
                    self.setItem(row, col, item)
        self.cargar_tamanos()

    def parse_number(self, text):
        """
        Convierte texto numérico (con comas, decimales o %) en un valor float para ordenamiento.
        
        Args:
            text (str): Texto que representa un valor numérico.
        
        Returns:
            float: Valor numérico convertido, o 0.0 si no se puede convertir.
        """
        try:
            text = text.replace(',', '').replace('%', '')
            return float(text)
        except ValueError:
            return 0.0

    def ordenar_columna(self, column):
        """
        Ordena la columna clicada, alternando entre orden ascendente y descendente.
        
        Args:
            column (int): Índice de la columna a ordenar.
        """
        if column not in self.sort_orders:
            self.sort_orders[column] = Qt.DescendingOrder
        else:
            self.sort_orders[column] = Qt.AscendingOrder if self.sort_orders[column] == Qt.DescendingOrder else Qt.DescendingOrder
        self.sortItems(column, self.sort_orders[column])
        self.horizontalHeader().setSortIndicator(column, self.sort_orders[column])

    def cargar_tamanos(self):
        """
        Carga los tamaños de columna guardados desde QSettings.
        """
        for col in range(self.columnCount()):
            width = self.settings.value(f"column_{col}", 100, type=int)
            self.setColumnWidth(col, width)

    def guardar_tamanos(self):
        """
        Guarda los tamaños de columna en QSettings al cerrar la tabla.
        """
        for col in range(self.columnCount()):
            self.settings.setValue(f"column_{col}", self.columnWidth(col))

    def closeEvent(self, event):
        """
        Ejecuta acciones al cerrar la tabla, como guardar los tamaños de columna.
        
        Args:
            event (QCloseEvent): Evento de cierre.
        """
        self.guardar_tamanos()
        super().closeEvent(event)

    def mostrar_menu_contextual(self, pos):
        """
        Muestra un menú contextual al hacer clic derecho sobre la tabla.
        
        Args:
            pos (QPoint): Posición donde se hizo clic derecho.
        """
        from gui.utils import show_news
        menu = QMenu(self)
        news_action = QAction("ℹ️ Ver Noticia", self)
        news_action.triggered.connect(lambda: show_news(self))
        menu.addAction(news_action)

        delete_action = QAction("🗑️ Eliminar", self)
        delete_action.triggered.connect(lambda: self.app.eliminar_seleccion())
        menu.addAction(delete_action)

        copy_action = QAction("📋 Copiar", self)
        copy_action.triggered.connect(self.copiar_seleccion)
        menu.addAction(copy_action)

        menu.exec_(self.mapToGlobal(pos))

    def copiar_seleccion(self):
        """
        Copia las celdas seleccionadas al portapapeles, separadas por tabuladores.
        """
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
        """
        Redirige la eliminación de filas seleccionadas al método del padre (ScreenerApp).
        """
        self.app.eliminar_seleccion()