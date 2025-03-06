from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QToolBar, QLabel, QAction, QStatusBar
from PyQt5.QtCore import Qt
import threading
from gui.widgets import Sidebar, DataTable
from gui.filters import FilterDialog
from gui.utils import export_to_csv

class ScreenerApp(QMainWindow):
    """Ventana principal de la aplicación Screener 2025."""
    def __init__(self):
        """Inicializa la ventana con barra de herramientas, tabla y barra de estado."""
        super().__init__()
        self.setWindowTitle("Screener 2025")
        self.setGeometry(100, 100, 1200, 700)
        self.setStyleSheet("background-color: #0e0f15; color: #ffffff;")

        toolbar = QToolBar("Herramientas")
        toolbar.setStyleSheet("background-color: #0e0f15; spacing: 10px;")
        self.addToolBar(Qt.TopToolBarArea, toolbar)
        update_action = QAction("🔄 Actualizar", self)
        update_action.triggered.connect(self.actualizar_datos)
        toolbar.addAction(update_action)
        filter_action = QAction("🔍 Filtrar", self)
        filter_action.triggered.connect(self.abrir_filtros)
        toolbar.addAction(filter_action)
        export_action = QAction("💾 Exportar", self)
        export_action.triggered.connect(self.exportar_datos)
        toolbar.addAction(export_action)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        stats_widget = QWidget()
        stats_layout = QHBoxLayout(stats_widget)
        stats_widget.setStyleSheet("background-color: #191a24; padding: 5px;")
        self.tickers_label = QLabel("Tickers: 0")
        self.cambio_label = QLabel("Cambio Promedio: 0%")
        stats_layout.addWidget(self.tickers_label)
        stats_layout.addWidget(self.cambio_label)
        stats_layout.addStretch()
        main_layout.addWidget(stats_widget)

        content_layout = QHBoxLayout()
        self.sidebar = Sidebar(self)
        content_layout.addWidget(self.sidebar, 1)
        self.table = DataTable(self)
        content_layout.addWidget(self.table, 4)
        main_layout.addLayout(content_layout)

        self.status_bar = QStatusBar()
        self.status_bar.setStyleSheet("background-color: #191a24; color: #ffffff;")
        self.setStatusBar(self.status_bar)
        self.table.itemSelectionChanged.connect(self.actualizar_estado)

        self.cargar_datos()

    def cargar_datos(self):
        """Carga datos iniciales desde la base de datos a la tabla."""
        from Base_Datos import conectar, leer_datos
        conn = conectar()
        if conn:
            datos = leer_datos(conn, "TablaFinviz")
            self.table.cargar_datos(datos)
            self.actualizar_estadisticas(datos)
            conn.close()

    def actualizar_datos(self):
        """Inicia un hilo para actualizar los datos y muestra el estado."""
        self.status_bar.showMessage("Iniciando actualización...")
        threading.Thread(target=self._actualizar_datos_thread, daemon=True).start()

    def _actualizar_datos_thread(self):
        """Actualiza los datos en la base y recarga la tabla, mostrando estados."""
        from main import buscar_tickers
        self.status_bar.showMessage("Actualizando datos...")
        buscar_tickers()
        self.cargar_datos()
        self.status_bar.showMessage("Actualización completada", 3000)  # Muestra por 3 segundos

    def abrir_filtros(self):
        """Abre la ventana de filtros y aplica los seleccionados."""
        dialog = FilterDialog(self)
        if dialog.exec_():
            filtros = dialog.obtener_filtros()
            self.aplicar_filtro(filtros)

    def aplicar_filtro(self, filtros):
        """Filtra los datos según los criterios seleccionados."""
        from Base_Datos import conectar, leer_datos
        conn = conectar()
        if conn:
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
            self.table.cargar_datos(datos)
            self.actualizar_estadisticas(datos)
            conn.close()

    def exportar_datos(self):
        """Exporta los datos de la tabla a un archivo CSV."""
        export_to_csv(self.table)

    def actualizar_estadisticas(self, datos):
        """Actualiza las estadísticas mostradas en el panel superior."""
        num_tickers = len(datos)
        cambio_total = sum(float(row[3].strip("%")) for row in datos if row[3]) / num_tickers if num_tickers > 0 else 0
        self.tickers_label.setText(f"Tickers: {num_tickers}")
        self.cambio_label.setText(f"Cambio Promedio: {cambio_total:.2f}%")

    def actualizar_estado(self):
        """Actualiza la barra de estado con el cambio de la fila seleccionada."""
        selected = self.table.selectedItems()
        if selected:
            cambio = self.table.item(selected[0].row(), 3).text()
            self.status_bar.showMessage(f"Cambio seleccionado: {cambio}")
        else:
            self.status_bar.showMessage("Selecciona una fila para ver el cambio")

    def eliminar_seleccion(self):
        """Elimina las filas seleccionadas de la tabla y la base de datos."""
        from Base_Datos import conectar, eliminar_datos
        selected = self.table.selectedItems()
        if not selected:
            self.status_bar.showMessage("No hay filas seleccionadas para eliminar")
            return

        tickers = {self.table.item(item.row(), 1).text() for item in selected}
        conn = conectar()
        if conn:
            eliminar_datos(conn, "TablaFinviz", list(tickers))
            self.cargar_datos()
            conn.close()

    def closeEvent(self, event):
        """Guarda los tamaños de columna al cerrar la ventana."""
        self.table.guardar_tamanos()
        super().closeEvent(event)