from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QAction, QStatusBar, QMenu, QProgressBar, QPushButton
from PyQt5.QtCore import Qt, QObject, pyqtSignal, QTimer, QThread, QPropertyAnimation, QSize, QRect
from PyQt5.QtGui import QIcon, QPixmap, QColor
import threading
import traceback
import time
from .widgets import DataTable
from .filters import FilterDialog
from .utils import export_to_csv
from Base_Datos import conectar, leer_datos
from archivo.main import buscar_tickers
from scraper_yahoo import main as actualizar_volumen_y_datos
from .table_customization import customize_table, apply_delegate, apply_custom_rounded

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

        # Configuración del widget central y layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)  # Reducir márgenes del layout principal
        main_layout.setSpacing(0)  # Reducir espaciado entre elementos

        # Layout horizontal para los botones (alineado a la izquierda)
        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignLeft)  # Alinear a la izquierda
        button_layout.setContentsMargins(5, 5, 0, 0)  # Márgenes mínimos
        button_layout.setSpacing(5)  # Espacio entre botones

        # Crear y escalar el ícono para el botón "Opciones"
        pixmap_options = QPixmap("C:/Users/Admin/Documents/Screener 2025/Option_icon.png")
        if pixmap_options.isNull():
            print("Error: No se pudo cargar el ícono de Opciones. Verifica la ruta o el archivo.")
        else:
            pixmap_options = pixmap_options.scaled(24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation)  # Tamaño pequeño
            print(f"Tamaño del pixmap (Opciones): {pixmap_options.size()}")  # Depuración
            icon_options = QIcon(pixmap_options)

            # Botón "Opciones" (solo ícono)
            self.options_button = QPushButton(self)
            self.options_button.setIcon(icon_options)
            self.options_button.setStyleSheet("""
                QPushButton { 
                    background-color: #0e0f15; 
                    border: 1px solid #0e0f15;  /* Borde azul claro */
                    padding: 2px; 
                }
                QPushButton:hover { 
                    background-color: #4a4a4a; 
                }
            """)
            self.options_button.setFixedSize(32, 32)  # Tamaño pequeño del botón
            self.options_button.clicked.connect(self.abrir_menu_opciones)

            # Eventos para animaciones
            self.options_button.enterEvent = self.on_enter_options
            self.options_button.leaveEvent = self.on_leave_options
            self.options_button.clicked.connect(self.on_click_options)

            button_layout.addWidget(self.options_button)

        # Crear y escalar el ícono para el botón "Filtrar"
        pixmap_filter = QPixmap("C:/Users/Admin/Documents/Screener 2025/Filter_icon.png")  # Ajusta la ruta
        if pixmap_filter.isNull():
            print("Error: No se pudo cargar el ícono de Filtrar. Verifica la ruta o el archivo.")
        else:
            pixmap_filter = pixmap_filter.scaled(24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation)  # Tamaño pequeño
            print(f"Tamaño del pixmap (Filtrar): {pixmap_filter.size()}")  # Depuración
            icon_filter = QIcon(pixmap_filter)

            # Botón "Filtrar" (solo ícono)
            self.filter_button = QPushButton(self)
            self.filter_button.setIcon(icon_filter)
            self.filter_button.setStyleSheet("""
                QPushButton { 
                    background-color: #0e0f15; 
                    border: 1px solid #1e90ff;  /* Borde azul claro */
                    padding: 2px; 
                }
                QPushButton:hover { 
                    background-color: #4a4a4a; 
                    border: 1px solid #63b8ff;  /* Borde azul más claro al pasar el mouse */
                }
            """)
            self.filter_button.setFixedSize(32, 32)  # Tamaño pequeño del botón
            self.filter_button.clicked.connect(self.abrir_filtros)

            # Eventos para animaciones
            self.filter_button.enterEvent = self.on_enter_filter
            self.filter_button.leaveEvent = self.on_leave_filter
            self.filter_button.clicked.connect(self.on_click_filter)

            button_layout.addWidget(self.filter_button)

        # Añadir el layout de botones al layout principal
        main_layout.addLayout(button_layout)

        # Tabla
        self.table = DataTable(self)
        main_layout.addWidget(self.table)

        # Barra de estado
        self.status_bar = QStatusBar()
        self.status_bar.setStyleSheet("background-color: #0e0f15; color: #ffffff;")
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
        apply_delegate(self.table, rounded_columns=[2, 3, 4], text_color="#00f4cf", background_color="#0e2524")
        rounded_styles = {
            1: {'background_color': '#1d1c44', 'text_color': '#aeddf1'},
            13: {'background_color': '#3a2c18', 'text_color': '#fef399'}
        }
        apply_custom_rounded(self.table, rounded_styles)
        apply_delegate(self.table)

    def on_enter_options(self, event):
        # Animación de escala al pasar el mouse (crecer)
        self.animate_button(self.options_button, QSize(40, 40), QSize(48, 48), 200)
        # Animación del color del borde
        self.animate_border_color(self.options_button, QColor("#efd700"), QColor("#63b8ff"), 200)

    def on_leave_options(self, event):
        # Animación de escala al salir del mouse (volver al tamaño original)
        self.animate_button(self.options_button, QSize(40, 40), QSize(32, 32), 200)
        # Animación del color del borde (volver al color original)
        self.animate_border_color(self.options_button, QColor("#da4b75"), QColor("#0e0f15"), 200)

    def on_click_options(self):
        # Animación de escala al hacer clic (efecto de pulsación)
        self.animate_button(self.options_button, QSize(32, 32), QSize(28, 28), 100, 
                           lambda: self.animate_button(self.options_button, QSize(28, 28), QSize(32, 32), 100))

    def on_enter_filter(self, event):
        # Animación de escala al pasar el mouse (crecer)
        self.animate_button(self.filter_button, QSize(32, 32), QSize(40, 40), 200)
        # Animación del color del borde
        self.animate_border_color(self.filter_button, QColor("#63b8ff"), QColor("#efd700"), 200)

    def on_leave_filter(self, event):
        # Animación de escala al salir del mouse (volver al tamaño original)
        self.animate_button(self.filter_button, QSize(40, 40), QSize(32, 32), 200)
        # Animación del color del borde (volver al color original)
        self.animate_border_color(self.filter_button, QColor("#efd700"), QColor("#1e90ff"), 200)

    def on_click_filter(self):
        # Animación de escala al hacer clic (efecto de pulsación)
        self.animate_button(self.filter_button, QSize(32, 32), QSize(28, 28), 100, 
                            lambda: self.animate_button(self.filter_button, QSize(28, 28), QSize(32, 32), 100))

    def animate_button(self, button, start_size, end_size, duration, on_finished=None):
        animation = QPropertyAnimation(button, b"geometry", self)
        start_geometry = button.geometry()
        end_geometry = QRect(
            start_geometry.x() - (end_size.width() - start_size.width()) // 2,
            start_geometry.y() - (end_size.height() - start_size.height()) // 2,
            end_size.width(),
            end_size.height()
        )
        animation.setStartValue(start_geometry)
        animation.setEndValue(end_geometry)
        animation.setDuration(duration)
        if on_finished:
            animation.finished.connect(on_finished)
        animation.start()

    def animate_border_color(self, button, start_color, end_color, duration):
        animation = QPropertyAnimation(button, b"borderColor", self)
        animation.setStartValue(start_color)
        animation.setEndValue(end_color)
        animation.setDuration(duration)
        animation.valueChanged.connect(lambda color: self.update_border_color(button, color))
        animation.start()

    def update_border_color(self, button, color):
        button.setStyleSheet(f"""
            QPushButton {{ 
                background-color: #0e0f15; 
                border: 1px solid {color.name()}; 
                padding: 2px; 
            }}
            QPushButton:hover {{ 
                background-color: #ffc600; 
            }}
        """)

    def abrir_menu_opciones(self):
        menu = QMenu(self)
        update_action = QAction("🔄 Actualizar", self)
        update_action.triggered.connect(self.actualizar_datos)
        menu.addAction(update_action)
        export_action = QAction("💾 Exportar", self)
        export_action.triggered.connect(self.exportar_datos)
        menu.addAction(export_action)
        button = self.sender()
        menu.exec_(button.mapToGlobal(button.rect().bottomLeft()))

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

if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    import sys
    app = QApplication(sys.argv)
    window = ScreenerApp()
    window.show()
    sys.exit(app.exec_())