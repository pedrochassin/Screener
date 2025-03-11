from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QMenuBar, QAction, QStatusBar, QMenu
from PyQt5.QtCore import Qt
import threading
from gui.widgets import Sidebar, DataTable
from gui.filters import FilterDialog
from gui.utils import export_to_csv

class ScreenerApp(QMainWindow):
    """Ventana principal de la aplicación Screener 2025."""
    def __init__(self):
        """Inicializa la ventana con menú desplegable y barra de estado."""
        super().__init__()
        self.setWindowTitle("Screener 2025")
        self.setGeometry(100, 100, 1200, 700)
        self.setStyleSheet("background-color: #1e1e1e; color: #ffffff;")

        # Menú desplegable superior con efecto hover
        menubar = self.menuBar()
        menubar.setStyleSheet("""
            QMenuBar {
                background-color: #2a2a2a;
                color: #ffffff;
            }
            QMenuBar::item {
                background-color: #2a2a2a;
                padding: 5px 10px;
            }
            QMenuBar::item:selected {
                background-color: #4a4a4a;
                color: #ffffff;
                transition: background-color 0.3s ease;
            }
            QMenu {
                background-color: #2a2a2a;
                color: #ffffff;
            }
            QMenu::item:selected {
                background-color: #4a4a4a;
            }
        """)
        file_menu = QMenu("Opciones", self)
        menubar.addMenu(file_menu)
        
        update_action = QAction("🔄 Actualizar", self)
        update_action.triggered.connect(self.actualizar_datos)
        file_menu.addAction(update_action)
        
        export_action = QAction("💾 Exportar", self)
        export_action.triggered.connect(self.exportar_datos)
        file_menu.addAction(export_action)

        filter_action = QAction("🔍 Filtrar", self)
        filter_action.triggered.connect(self.abrir_filtros)
        menubar.addAction(filter_action)

        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        content_layout = QHBoxLayout()
        self.sidebar = Sidebar(self)
        content_layout.addWidget(self.sidebar, 1)
        self.table = DataTable(self)  # Pasamos self (ScreenerApp) como parent
        content_layout.addWidget(self.table, 4)
        main_layout.addLayout(content_layout)

        # Barra de estado
        self.status_bar = QStatusBar()
        self.status_bar.setStyleSheet("background-color: #2a2a2a; color: #ffffff;")
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
        self.status_bar.showMessage("Actualización completada", 3000)

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
            conn.close()

    def exportar_datos(self):
        """Exporta los datos de la tabla a un archivo CSV."""
        export_to_csv(self.table)

    def actualizar_estado(self):
        """Actualiza la barra de estado con el cambio de la fila seleccionada."""
        selected = self.table.selectedItems()
        if selected:
            cambio = self.table.item(selected[0].row(), 3).text()
            self.status_bar.showMessage(f"Cambio seleccionado: {cambio}")
        else:
            self.status_bar.showMessage("Selecciona una fila para ver el cambio")

    def eliminar_seleccion(self):
        """Elimina las filas seleccionadas y recarga los datos."""
        from Base_Datos import conectar, eliminar_datos
        selected = self.table.selectedItems()
        if not selected:
            self.status_bar.showMessage("No hay filas seleccionadas para eliminar")
            return

        tickers = {self.table.item(item.row(), 1).text() for item in selected}
        conn = conectar()
        if conn:
            eliminar_datos(conn, "TablaFinviz", list(tickers))
            conn.close()
            self.cargar_datos()
        else:
            self.status_bar.showMessage("Error al conectar a la base de datos")

    def closeEvent(self, event):
        """Guarda los tamaños de columna al cerrar la ventana."""
        self.table.guardar_tamanos()
        super().closeEvent(event)