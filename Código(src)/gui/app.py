from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QMenuBar, QAction, QStatusBar, QMenu, QProgressBar
from PyQt5.QtCore import Qt, QObject, pyqtSignal, QTimer, QThread
import threading
import traceback
import time
from .widgets import DataTable
from .filters import FilterDialog
from .utils import export_to_csv
from Base_Datos import conectar, leer_datos
from archivo.main import buscar_tickers
from scraper_yahoo import main as actualizar_volumen_y_datos
from .table_customization import customize_table, apply_delegate, apply_custom_rounded  # Importar funciones de personalización

class WorkerSignals(QObject):
    progress = pyqtSignal(int)
    message = pyqtSignal(str)
    finished = pyqtSignal()
    error = pyqtSignal(str)

class WorkerActualizarDatos(QObject):
    progress = pyqtSignal(int)
    message = pyqtSignal(str)
    finished = pyqtSignal()
    error = pyqtSignal(str)

    def run(self):
        try:
            self.message.emit("Iniciando actualización de datos...")
            self.progress.emit(0)
            time.sleep(0.01)

            for i in range(0, 20, 2):
                self.progress.emit(i)
                time.sleep(0.02)

            self.message.emit("Actualizando datos...")
            buscar_tickers()
            for i in range(20, 50, 2):
                self.progress.emit(i)
                time.sleep(0.05)

            self.message.emit("Actualizando volumen y datos históricos...")
            time.sleep(0.01)

            for i in range(50, 70, 2):
                self.progress.emit(i)
                time.sleep(0.02)

            actualizar_volumen_y_datos()
            for i in range(70, 100, 2):
                self.progress.emit(i)
                time.sleep(0.05)

            self.finished.emit()
        except Exception as e:
            error_msg = f"Error durante la actualización: {str(e)}\n{traceback.format_exc()}"
            self.error.emit(error_msg)

class ScreenerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Screener 2025")
        self.setGeometry(100, 100, 1200, 700)
        self.setStyleSheet("background-color: #0e0f15; color: #ffffff;")

        menubar = self.menuBar()
        menubar.setStyleSheet("""
            QMenuBar { background-color: #0e0f15; color: #ffffff; }
            QMenuBar::item { background-color: #0e0f15; padding: 5px 10px; }
            QMenuBar::item:selected { background-color: #4a4a4a; color: #ffffff; transition: background-color 0.3s ease; }
            QMenu { background-color: #0e0f15; color: #ffffff; }
            QMenu::item:selected { background-color: #4a4a4a; }
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

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        self.table = DataTable(self)
        main_layout.addWidget(self.table)

        self.status_bar = QStatusBar()
        self.status_bar.setStyleSheet("background-color: #2a2a2a; color: #ffffff;")
        self.setStatusBar(self.status_bar)
        self.table.itemSelectionChanged.connect(self.actualizar_estado)

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setStyleSheet("QProgressBar { border: 1px solid #4a4a4a; background-color: #3a3a3a; color: #ffffff; text-align: center; } QProgressBar::chunk { background-color: #1e90ff; }")
        self.progress_bar.setMaximumWidth(200)
        self.progress_bar.setVisible(False)
        self.status_bar.addPermanentWidget(self.progress_bar)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.cargar_datos)
        self.update_count = 0
        self.max_updates = 2

        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.cargar_datos)
        self.refresh_timer.start(100000)

        self.cargar_datos()
        # Redondeado condicional a la fecha (opcional, si aún lo quieres)
        apply_delegate(self.table, rounded_columns=[2, 3, 4], text_color="#00f4cf", background_color="#0e2524")
        # Redondeados independientes con estilos por columna
        rounded_styles = {
            1: {'background_color': '#1d1c44', 'text_color': '#aeddf1'},  # Columna 1: fondo rojo, texto blanco
           13: {'background_color': '#3a2c18', 'text_color': '#fef399'}   # Columna 7: fondo azul, texto amarillo
        }
        apply_custom_rounded(self.table, rounded_styles)
        apply_delegate(self.table)  # Aplicar el delegado a la tabla

    def cargar_datos(self):
        if self.update_count >= self.max_updates and not self.refresh_timer.isActive():
            self.timer.stop()
            self.status_bar.showMessage("Número máximo de actualizaciones alcanzado", 5000)
            return

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
                self.table.cargar_datos(datos)
                column_styles = {
                    1: {'bold': True},  # Columna 1 en negrita
                    2: {'align': Qt.AlignCenter},  # Columna 2 centrada
                    3: {'align': Qt.AlignCenter},  # Columna 3 centrada y texto rojo
                    4: {'align': Qt.AlignCenter},
                    6: {'bold': True},  # Columna 6 en negrita y texto verde
                    11: {'align': Qt.AlignCenter},
                    18: {'align': Qt.AlignCenter},
                    19: {'align': Qt.AlignCenter},
                    13: {'bold': True,'align': Qt.AlignCenter, 'color': '#00f4cf'},  # Columna 13 centrada y texto rojo
                }
                customize_table(self.table, column_styles)

            except Exception as e:
                self.status_bar.showMessage(f"Error al cargar datos: {str(e)}", 10000)
            finally:
                conn.close()

        self.update_count += 1

    def actualizar_datos(self):
        self.status_bar.showMessage("Iniciando actualización completa...")
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.thread = QThread()
        self.worker = WorkerActualizarDatos()
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.progress.connect(self.progress_bar.setValue)
        self.worker.message.connect(self.status_bar.showMessage)
        self.worker.finished.connect(self._actualizacion_completada)
        self.worker.error.connect(self._mostrar_error)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.start()

    def _actualizacion_completada(self):
        self.status_bar.showMessage("Actualización completa finalizada", 3000)
        self.progress_bar.setValue(100)
        self.progress_bar.setVisible(False)
        self.update_count = 0
        self.cargar_datos()
        if not self.refresh_timer.isActive():
            self.refresh_timer.start(300000)

    def _mostrar_error(self, error_msg):
        self.status_bar.showMessage(error_msg, 10000)
        print(error_msg)
        self.progress_bar.setVisible(False)
        self.timer.stop()

    def abrir_filtros(self):
        dialog = FilterDialog(self)
        if dialog.exec_():
            filtros = dialog.obtener_filtros()
            self.aplicar_filtro(filtros)

    def aplicar_filtro(self, filtros):
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
                self.table.cargar_datos(datos)
            except Exception as e:
                self.status_bar.showMessage(f"Error al aplicar filtro: {str(e)}", 10000)
            finally:
                conn.close()

    def exportar_datos(self):
        export_to_csv(self.table)

    def actualizar_estado(self):
        selected = self.table.selectedItems()
        if selected:
            cambio = self.table.item(selected[0].row(), 3).text()
            self.status_bar.showMessage(f"Cambio seleccionado: {cambio}")
        else:
            self.status_bar.showMessage("Selecciona una fila para ver el cambio")

    def eliminar_seleccion(self):
        from Base_Datos import conectar, eliminar_datos
        selected = self.table.selectedItems()
        if not selected:
            self.status_bar.showMessage("No hay filas seleccionadas para eliminar")
            return
        tickers = {self.table.item(item.row(), 1).text() for item in selected}
        conn = conectar()
        if conn:
            try:
                eliminar_datos(conn, "TablaFinviz", list(tickers))
                self.cargar_datos()
            except Exception as e:
                self.status_bar.showMessage(f"Error al eliminar selección: {str(e)}", 10000)
            finally:
                conn.close()

    def closeEvent(self, event):
        self.timer.stop()
        self.refresh_timer.stop()
        self.table.guardar_tamanos()
        super().closeEvent(event)