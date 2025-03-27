from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QAction, QStatusBar, QMenu, QProgressBar, QPushButton
from PyQt5.QtCore import Qt, QObject, pyqtSignal, QTimer, QThread, QPropertyAnimation, QSize, QRect
from PyQt5.QtGui import QIcon, QPixmap, QColor
import threading, traceback, time
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

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignLeft)
        button_layout.setContentsMargins(5, 5, 0, 0)
        button_layout.setSpacing(5)

        pixmap_options = QPixmap("C:/Users/Admin/Documents/Screener 2025/Option_icon.png")
        if pixmap_options.isNull():
            print("Error: No se pudo cargar el ícono de Opciones. Verifica la ruta o el archivo.")
        else:
            pixmap_options = pixmap_options.scaled(24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            icon_options = QIcon(pixmap_options)

            self.options_button = QPushButton(self)
            self.options_button.setIcon(icon_options)
            self.options_button.setStyleSheet("""
                QPushButton { 
                    background-color: #0e0f15; 
                    border: 1px solid #0e0f15;
                    padding: 2px; 
                }
                QPushButton:hover { 
                    background-color: #4a4a4a; 
                }
            """)
            self.options_button.setFixedSize(32, 32)
            self.options_button.clicked.connect(self.abrir_menu_opciones)
            self.options_button.enterEvent = self.on_enter_options
            self.options_button.leaveEvent = self.on_leave_options
            self.options_button.clicked.connect(self.on_click_options)
            button_layout.addWidget(self.options_button)

        pixmap_filter = QPixmap("C:/Users/Admin/Documents/Screener 2025/Filter_icon.png")
        if pixmap_filter.isNull():
            print("Error: No se pudo cargar el ícono de Filtrar. Verifica la ruta o el archivo.")
        else:
            pixmap_filter = pixmap_filter.scaled(24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            icon_filter = QIcon(pixmap_filter)

            self.filter_button = QPushButton(self)
            self.filter_button.setIcon(icon_filter)
            self.filter_button.setStyleSheet("""
                QPushButton { 
                    background-color: #0e0f15; 
                    border: 1px solid #0e0f15;
                    padding: 2px; 
                }
                QPushButton:hover { 
                    background-color: #4a4a4a; 
                    border: 1px solid #63b8ff;
                }
            """)
            self.filter_button.setFixedSize(32, 32)
            self.filter_button.clicked.connect(self.abrir_filtros)
            self.filter_button.enterEvent = self.on_enter_filter
            self.filter_button.leaveEvent = self.on_leave_filter
            self.filter_button.clicked.connect(self.on_click_filter)
            button_layout.addWidget(self.filter_button)

        main_layout.addLayout(button_layout)

        self.table = DataTable(self)
        main_layout.addWidget(self.table)

        self.status_bar = QStatusBar()
        self.status_bar.setStyleSheet("background-color: #0e0f15; color: #ffffff;")
        self.setStatusBar(self.status_bar)
        self.table.itemSelectionChanged.connect(self.actualizar_estado)

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setStyleSheet("""
            QProgressBar { 
                border: 1px solid #4a4a4a; 
                background-color: #3a3a3a; 
                color: #ffffff; 
                text-align: center; 
            } 
            QProgressBar::chunk { 
                background-color: #1e90ff; 
            }
        """)
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
        self.animate_button(self.options_button, QSize(40, 40), QSize(48, 48), 200)
        self.animate_border_color(self.options_button, QColor("#efd700"), QColor("#63b8ff"), 200)

    def on_leave_options(self, event):
        self.animate_button(self.options_button, QSize(40, 40), QSize(32, 32), 200)
        self.animate_border_color(self.options_button, QColor("#da4b75"), QColor("#0e0f15"), 200)

    def on_click_options(self):
        self.animate_button(self.options_button, QSize(32, 32), QSize(28, 28), 100, 
                           lambda: self.animate_button(self.options_button, QSize(28, 28), QSize(32, 32), 100))

    def on_enter_filter(self, event):
        self.animate_button(self.filter_button, QSize(32, 32), QSize(40, 40), 200)
        self.animate_border_color(self.filter_button, QColor("#63b8ff"), QColor("#efd700"), 200)

    def on_leave_filter(self, event):
        self.animate_button(self.filter_button, QSize(40, 40), QSize(32, 32), 200)
        self.animate_border_color(self.filter_button, QColor("#efd700"), QColor("#0e0f15"), 200)

    def on_click_filter(self):
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

    def guardar_estado_tabla(self):
        """Guarda el estado actual de la tabla antes de una actualización."""
        header = self.table.horizontalHeader()
        
        # Guardar selección
        seleccion = self.table.selectedIndexes()
        self.estado_seleccion = [(index.row(), index.column()) for index in seleccion] if seleccion else []
        
        # Guardar ordenamiento
        self.estado_orden = {
            'columna': header.sortIndicatorSection(),
            'orden': header.sortIndicatorOrder()
        }
        
        # Guardar posición de las columnas
        self.estado_posiciones = [header.logicalIndex(i) for i in range(header.count())]
        
        # Guardar scroll position
        self.estado_scroll = {
            'vertical': self.table.verticalScrollBar().value(),
            'horizontal': self.table.horizontalScrollBar().value()
        }

    def restaurar_estado_tabla(self):
        """Restaura el estado de la tabla después de una actualización."""
        header = self.table.horizontalHeader()
        
        # Restaurar posición de las columnas
        if hasattr(self, 'estado_posiciones'):
            for visual_index, logical_index in enumerate(self.estado_posiciones):
                header.moveSection(header.visualIndex(logical_index), visual_index)
        
        # Restaurar ordenamiento
        if hasattr(self, 'estado_orden') and self.estado_orden['columna'] is not None:
            self.table.sortItems(self.estado_orden['columna'], self.estado_orden['orden'])
            header.setSortIndicator(self.estado_orden['columna'], self.estado_orden['orden'])
        
        # Restaurar selección
        if hasattr(self, 'estado_seleccion'):
            self.table.clearSelection()
            for row, col in self.estado_seleccion:
                if row < self.table.rowCount() and col < self.table.columnCount():
                    self.table.setItemSelected(self.table.item(row, col), True)
        
        # Restaurar scroll position
        if hasattr(self, 'estado_scroll'):
            self.table.verticalScrollBar().setValue(self.estado_scroll['vertical'])
            self.table.horizontalScrollBar().setValue(self.estado_scroll['horizontal'])

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

        # Guardar estado actual de la tabla
        self.guardar_estado_tabla()

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

                # Restaurar estado de la tabla
                self.restaurar_estado_tabla()

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
        self.cargar_datos()  # Esto ya incluye guardar/restaurar estado
        if not self.refresh_timer.isActive():
            self.refresh_timer.start(1000)

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