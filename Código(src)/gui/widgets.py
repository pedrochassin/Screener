from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit, QMenu, QApplication, QAction, QProgressBar
from PyQt5.QtCore import Qt, QSettings, QUrl
from PyQt5.QtGui import QDesktopServices  # Para abrir enlaces en el navegador

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
    """Tabla personalizada para mostrar datos con ordenamiento, filtrado, menú contextual y enlaces en Ticker."""
    
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
            "ShsFloat", "ShortFloat", "ShortRatio", "AvgVolume", "CashSh", "VolumenActual", "Open", "Close", "High", "Low", "Rvol", "Return"
        ])  # Encabezados de las columnas
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.horizontalHeader().setMinimumSectionSize(50)
        self.horizontalHeader().setSectionsMovable(True)  # Permitir mover columnas
        self.horizontalHeader().sectionMoved.connect(self.guardar_posiciones_columnas)  # Conectar señal para guardar posiciones

        # Estilo de la tabla, incluyendo el corner button
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
            QTableWidget::item:hover {
                background-color: #2a2c3c;  /* Fondo al pasar el mouse */
            }
            QTableWidget::item:selected {
                background-color: #63b8ff;  /* Fondo de celdas seleccionadas */
            }
            QTableCornerButton::section {
                background-color: #232533;  /* Fondo de la esquina superior izquierda (mismo que el header) */
                border: 1px solid #0e0f15;  /* Borde de la esquina */
            }
            QProgressBar {
                border: none;
                background-color: #232533;
                border-radius: 5px;
                text-align: center;
                color: #232533; /* Color del texto dentro de la barra de progreso */
            }
            QProgressBar::chunk {
                background: qlineargradient(
                spread:pad, 
                x1:0, y1:0, x2:1, y2:0, 
                stop:0 #00cc00,   /* Verde claro */
                stop:0.5 #ffff00, /* Amarillo */
                stop:1 #ff0000    /* Rojo */
    );
    border-radius: 5px;
}

        """)
        self.setEditTriggers(QTableWidget.NoEditTriggers)  # Desactiva edición directa
        self.horizontalHeader().sectionClicked.connect(self.ordenar_columna)
        self.verticalHeader().setStyleSheet("background-color: #0e0f15; color: #ffffff;")
        self.sort_orders = {}  # Diccionario para almacenar el orden de cada columna
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.mostrar_menu_contextual)
        
        # Conectar el evento de doble clic para abrir enlaces
        self.cellDoubleClicked.connect(self.abrir_enlace_ticker)

        self.filter_input = QLineEdit(self)
        self.filter_input.setPlaceholderText("Filtrar por Ticker...")
        self.filter_input.setStyleSheet("background-color: #0e0f15; color: #ffffff; padding: 5px;")
        self.filter_input.textChanged.connect(self.filtrar_en_tiempo_real)
        self.filter_input.setMaximumWidth(200)
        self.filter_input.move(10, 10)

        self.settings = QSettings("Screener2025", "TableSettings")
        self.cargar_tamanos()
        self.cargar_posiciones_columnas()  # Cargar posiciones de columnas al iniciar

    def cargar_datos(self, datos):
        """
        Carga datos desde la base de datos en la tabla y agrega enlaces a la columna Ticker.
        También inserta barras de progreso en la columna "Vacío" basadas en "Rvol".
        
        Args:
            datos (list): Lista de filas con datos obtenidos de la base de datos.
        """
        self.datos_completos = datos
        self.setRowCount(0)

        # Usar un valor fijo para normalizar las barras de progreso
        max_rvol = 5000.0  # Valor fijo para la normalización

        # Cargar los datos y añadir barras de progreso
        for fila in datos:
            row = self.rowCount()
            self.insertRow(row)
            for col, value in enumerate(fila):
                if col == 5:  # Columna "Vacío" (índice 5)
                    try:
                        rvol = float(fila[18])  # Columna Rvol (índice 18)
                    except (ValueError, TypeError):
                        rvol = 0.0
                    # Normalizar el valor de Rvol al rango 0-100
                    progress_value = min((rvol / max_rvol) * 100, 100) if max_rvol > 0 else 0
                    progress_bar = QProgressBar(self)
                    progress_bar.setValue(int(progress_value))
                    
                    progress_bar.setFixedHeight(15)  # Ajustar la altura de la barra
                    self.setCellWidget(row, col, progress_bar)
                    continue  # Saltar la creación de un QTableWidgetItem para esta celda
                if col == 1:  # Columna Ticker (índice 1)
                    item = QTableWidgetItem(str(value))  # Mostrar el nombre del ticker
                    # Construir el enlace para el ticker
                    enlace = f"https://app.flash-research.com" #/stock/{value}
                    item.setData(Qt.UserRole, enlace)  # Almacenar el enlace en Qt.UserRole
                    item.setToolTip(f"Haz doble clic para visitar {enlace}")  # Mostrar enlace como tooltip
                elif col == 13:  # Columna VolumenActual
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
        También inserta barras de progreso en la columna "Vacío" basadas en "Rvol".
        
        Args:
            texto (str): Texto ingresado por el usuario para filtrar por Ticker.
        """
        self.setRowCount(0)

        # Obtener el valor máximo de Rvol para normalizar las barras de progreso
        rvol_values = []
        for fila in self.datos_completos:
            if texto.lower() in str(fila[1]).lower():
                try:
                    rvol = float(fila[18])  # Columna Rvol (índice 18)
                    rvol_values.append(rvol)
                except (ValueError, TypeError):
                    rvol_values.append(0.0)
        max_rvol = max(rvol_values, default=1.0)  # Evitar división por cero

        # Filtrar y cargar los datos con barras de progreso
        for fila in self.datos_completos:
            if texto.lower() in str(fila[1]).lower():
                row = self.rowCount()
                self.insertRow(row)
                for col, value in enumerate(fila):
                    if col == 5:  # Columna "Vacío" (índice 5)
                        try:
                            rvol = float(fila[18])  # Columna Rvol (índice 18)
                        except (ValueError, TypeError):
                            rvol = 0.0
                        # Normalizar el valor de Rvol al rango 0-100
                        progress_value = (rvol / max_rvol) * 100 if max_rvol > 0 else 0
                        progress_bar = QProgressBar(self)
                        progress_bar.setValue(int(progress_value))
                        progress_bar.setTextVisible(False)  # Ocultar el texto del porcentaje
                        progress_bar.setFixedHeight(15)  # Ajustar la altura de la barra
                        self.setCellWidget(row, col, progress_bar)
                        continue  # Saltar la creación de un QTableWidgetItem para esta celda
                    if col == 1:  # Columna Ticker (índice 1)
                        item = QTableWidgetItem(str(value))  # Mostrar el nombre del ticker
                        # Construir el enlace para el ticker
                        enlace = f"https://app.flash-research.com" #/stock/{value}
                        item.setData(Qt.UserRole, enlace)  # Almacenar el enlace en Qt.UserRole
                        item.setToolTip(f"Haz doble clic para visitar {enlace}")  # Mostrar enlace como tooltip
                    elif col == 13:  # Columna VolumenActual
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

    def guardar_posiciones_columnas(self):
        """
        Guarda las posiciones actuales de las columnas en QSettings.
        """
        header = self.horizontalHeader()
        posiciones = [header.logicalIndex(i) for i in range(header.count())]
        self.settings.setValue("column_positions", posiciones)

    def cargar_posiciones_columnas(self):
        """
        Carga las posiciones de las columnas desde QSettings.
        """
        posiciones = self.settings.value("column_positions", None)
        if posiciones:
            # Asegurarse de que las posiciones sean una lista de enteros
            posiciones = [int(pos) for pos in posiciones]
            header = self.horizontalHeader()
            for visual_index, logical_index in enumerate(posiciones):
                header.moveSection(header.visualIndex(logical_index), visual_index)

    def closeEvent(self, event):
        """
        Ejecuta acciones al cerrar la tabla, como guardar los tamaños y posiciones de las columnas.
        
        Args:
            event (QCloseEvent): Evento de cierre.
        """
        self.guardar_tamanos()
        self.guardar_posiciones_columnas()
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

    def abrir_enlace_ticker(self, row, col):
        """
        Abre el enlace asociado al ticker en la columna 1 al hacer doble clic.
        
        Args:
            row (int): Fila de la celda clicada.
            col (int): Columna de la celda clicada.
        """
        if col == 1:  # Solo abrir enlace si se hace doble clic en la columna Ticker
            item = self.item(row, col)
            if item:
                enlace = item.data(Qt.UserRole)  # Obtener el enlace almacenado
                if enlace:
                    QDesktopServices.openUrl(QUrl(enlace))  # Abrir el enlace en el navegador