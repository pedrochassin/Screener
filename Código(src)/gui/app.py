from PyQt5.QtWidgets import QMainWindow, QAction, QMenu, QApplication, QDialog, QTableWidget, QTableWidgetItem, QVBoxLayout, QPushButton, QProgressBar, QAbstractButton, QHeaderView
from PyQt5.QtCore import QThread, Qt, QPropertyAnimation, QTimer, QSettings
from PyQt5.QtGui import QIcon
import sys
import pyodbc
from .workers import WorkerSignals, WorkerActualizarTickers, WorkerActualizarVolumenDatos
from .ui_components import setup_ui
from .animations import (on_enter_options, on_leave_options, on_click_options,
                        on_enter_filter, on_leave_filter, on_click_filter)
from .data_handlers import (cargar_datos, aplicar_filtro, exportar_datos,
                           actualizar_estado, eliminar_seleccion)
from Base_Datos import conectar
from .widgets import DataTable
from .animations import animate_button, animate_border_color
from .table_customization import apply_delegate, apply_custom_rounded

class DatosActualesWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(self.windowFlags() | Qt.WindowMaximizeButtonHint)
        self.setWindowTitle("Datos Actuales")
        self.setGeometry(200, 200, 800, 600)
        self.setStyleSheet("background-color: #0e0f15; color: #ffffff;")

        # Lista para mantener referencias
        self.progress_bars = []
        self.animations = []

        # Configuración de QSettings
        self.settings = QSettings("Screener2025", "DatosActualesTable")
        print(f"[DEBUG] QSettings file: {self.settings.fileName()}")

        # Layout principal
        layout = QVBoxLayout()

        # Usar QTableWidget
        self.table = QTableWidget(self)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #1a1b23;
                color: #ffffff;
                selection-background-color: #232533;
            }
            QTableWidget::item:hover {
                background-color: #2a2c3c;
            }
            QTableWidget::item:selected {
                background-color: #63b8ff;
            }
            QTableCornerButton::section {
                background-color: #232533;
                border: 1px solid #0e0f15;
            }
            QHeaderView::section:vertical {
                background-color: #232533;
                color: #ffffff;
                border: 1px solid #0e0f15;
            }
        """)
        # Habilitar movimiento de columnas
        self.table.horizontalHeader().setSectionsMovable(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.table.horizontalHeader().sectionMoved.connect(self.guardar_posiciones_columnas)
        layout.addWidget(self.table)

        # Botón cerrar
        close_button = QPushButton("Cerrar")
        close_button.setStyleSheet("""
            QPushButton {
                background-color: #2a2b33;
                color: #ffffff;
                padding: 5px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #3a3b43;
            }
        """)
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button)

        self.setLayout(layout)

        # Cargar datos
        self.cargar_datos()

        # Personalizar tabla
        self.personalizar_tabla()

        # Forzar estilos
        self.table.horizontalHeader().setStyleSheet("""
            QHeaderView::section {
                background-color: #232533;
                color: #ffffff;
                padding: 5px;
                border: 1px solid #0e0f15;
            }
        """)
        self.table.verticalHeader().setStyleSheet("""
            QHeaderView::section {
                background-color: #232533;
                color: #ffffff;
                border: 1px solid #0e0f15;
            }
        """)
        self.table.setStyleSheet(self.table.styleSheet() + """
            QTableCornerButton::section {
                background-color: #232533;
                border: 1px solid #0e0f15;
            }
        """)
        print("[DEBUG] Estilo de esquina, encabezados horizontal y vertical aplicado")

        # Cargar posiciones y tamaños de columnas
        self.cargar_posiciones_columnas()
        self.cargar_tamanos_columnas()

    def personalizar_tabla(self):
        """Aplica personalización a la tabla."""
        print("[DEBUG] Aplicando personalización de tabla...")
        apply_delegate(self.table, rounded_columns=[2, 3, 4, 5, 6], text_color="#00f4cf", background_color="#0e2524")
        rounded_styles = {
            1: {'background_color': '#1d1c44', 'text_color': '#aeddf1'},
            5: {'background_color': '#3a2c18', 'text_color': '#fef399'}
        }
        apply_custom_rounded(self.table, rounded_styles)
        print("[DEBUG] Personalización de tabla completa")

    def guardar_posiciones_columnas(self):
        """Guarda las posiciones actuales de las columnas en QSettings."""
        header = self.table.horizontalHeader()
        posiciones = [header.logicalIndex(i) for i in range(header.count())]
        self.settings.setValue("column_positions", posiciones)
        print("[DEBUG] Posiciones de columnas guardadas:", posiciones)

    def cargar_posiciones_columnas(self):
        """Carga las posiciones de las columnas desde QSettings."""
        posiciones = self.settings.value("column_positions", None)
        if posiciones:
            posiciones = [int(pos) for pos in posiciones]
            header = self.table.horizontalHeader()
            for visual_index, logical_index in enumerate(posiciones):
                header.moveSection(header.visualIndex(logical_index), visual_index)
            print("[DEBUG] Posiciones de columnas cargadas:", posiciones)

    def guardar_tamanos_columnas(self):
        """Guarda los tamaños de las columnas en QSettings."""
        for col in range(self.table.columnCount()):
            self.settings.setValue(f"column_{col}", self.table.columnWidth(col))
        print("[DEBUG] Tamaños de columnas guardados")

    def cargar_tamanos_columnas(self):
        """Carga los tamaños de las columnas desde QSettings."""
        for col in range(self.table.columnCount()):
            width = self.settings.value(f"column_{col}", 100, type=int)
            self.table.setColumnWidth(col, width)
        print("[DEBUG] Tamaños de columnas cargados")

    def cargar_datos(self):
        """Carga datos desde la base de datos en la tabla."""
        try:
            conn = conectar()
            if conn:
                cursor = conn.cursor()
                cursor.execute("SELECT Ticker, Price, [Change%], Volume, AvgVol, Rvo, Ret, RvoBar FROM DatosActuales")
                datos = cursor.fetchall()
                cursor.close()
                conn.close()
                print(f"[DEBUG] Cargadas {len(datos)} filas desde DatosActuales")

                # Calcular max_rvo
                valid_rvos = [float(row[5]) for row in datos if row[5] is not None and float(row[5]) > 0]
                max_rvo = max(valid_rvos, default=1000.0)
                print(f"[DEBUG] max_rvo calculado: {max_rvo}")

                # Configurar la tabla
                self.table.setRowCount(len(datos))
                self.table.setColumnCount(8)
                self.table.setHorizontalHeaderLabels(['Ticker', 'Price', 'Change%', 'Volume', 'AvgVol', 'Rvo', 'Ret', 'RvoBar'])

                # Desactivar actualizaciones para mejorar rendimiento
                self.table.setUpdatesEnabled(False)

                for row_idx, row_data in enumerate(datos):
                    for col_idx, value in enumerate(row_data):
                        if col_idx == 7:  # RvoBar
                            try:
                                rvo_raw = row_data[5]  # Rvo en col_idx 5
                                print(f"[DEBUG] Fila {row_idx}, Rvo raw: {rvo_raw}, Type: {type(rvo_raw)}")
                                if rvo_raw is None or rvo_raw == '':
                                    rvo = 0.0
                                    print(f"[DEBUG] Fila {row_idx}, Rvo es None o '', usando 0.0")
                                else:
                                    try:
                                        rvo = float(str(rvo_raw).strip())
                                        print(f"[DEBUG] Fila {row_idx}, Rvo convertido: {rvo}")
                                    except ValueError:
                                        rvo = 0.0
                                        print(f"[DEBUG] Fila {row_idx}, Error al convertir Rvo, usando 0.0")
                                rvo_normalized = min(max(rvo, 0), max_rvo)
                                progress = int(min(rvo_normalized / max_rvo, 1) * 80)  # Escala a 0-100
                                print(f"[DEBUG] Fila {row_idx}, Rvo normalizado: {rvo_normalized}, Progress: {progress}")

                                # Crear barra de progreso
                                progress_bar = QProgressBar()
                                progress_bar.setMinimum(0)
                                progress_bar.setMaximum(100)
                                progress_bar.setValue(0)  # Iniciar en 0
                                progress_bar.setTextVisible(False)
                                progress_bar.setFixedHeight(16)

                                # Estilo dinámico
                                if rvo <= 2:
                                    gradient = "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #00cc66, stop:1 #00ff99)"
                                elif rvo <= 4:
                                    gradient = "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #ffcc00, stop:1 #ffff66)"
                                else:
                                    gradient = "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #ff3333, stop:1 #ff6666)"

                                progress_bar.setStyleSheet(f"""
                                    QProgressBar {{
                                        background-color: #2a2b33;
                                        border: 1px solid #3a3b43;
                                        border-radius: 4px;
                                    }}
                                    QProgressBar::chunk {{
                                        background: {gradient};
                                        border-radius: 3px;
                                    }}
                                """)
                                print(f"[DEBUG] Fila {row_idx}, Estilo de barra aplicado")

                                # Tooltip
                                progress_bar.setToolTip(f"Rvo: {rvo:.2f}")

                                # Animación con respaldo
                                def set_progress_with_timer(bar, target):
                                    current = bar.value()
                                    if current < target:
                                        bar.setValue(current + 1)
                                        QTimer.singleShot(5, lambda: set_progress_with_timer(bar, target))
                                    else:
                                        bar.setValue(target)
                                        print(f"[DEBUG] Fila {row_idx}, Valor final: {bar.value()}")

                                progress_bar.setValue(progress)  # Intento directo
                                print(f"[DEBUG] Fila {row_idx}, Valor establecido: {progress_bar.value()}")
                                if progress_bar.value() != progress:
                                    print(f"[DEBUG] Fila {row_idx}, Animación con timer iniciada")
                                    QTimer.singleShot(0, lambda: set_progress_with_timer(progress_bar, progress))
                                else:
                                    print(f"[DEBUG] Fila {row_idx}, Animación no necesaria")

                                # Forzar actualización
                                progress_bar.repaint()

                                # Guardar referencias
                                self.progress_bars.append(progress_bar)
                                self.table.setCellWidget(row_idx, col_idx, progress_bar)
                                print(f"[DEBUG] Fila {row_idx}, Barra establecida en celda")
                            except Exception as e:
                                print(f"[DEBUG] Error al procesar RvoBar en fila {row_idx}: {e}")
                                item = QTableWidgetItem('')
                                self.table.setItem(row_idx, col_idx, item)
                        else:
                            item = QTableWidgetItem(str(value) if value is not None else '')
                            item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                            self.table.setItem(row_idx, col_idx, item)

                self.table.resizeColumnsToContents()
                self.table.setColumnWidth(7, 120)  # Ancho fijo para RvoBar

                # Reactivar actualizaciones
                self.table.setUpdatesEnabled(True)
                self.table.update()
        except Exception as e:
            print(f"[DEBUG] Error al cargar datos: {e}")

    def closeEvent(self, event):
        """Guarda configuraciones al cerrar."""
        self.guardar_posiciones_columnas()
        self.guardar_tamanos_columnas()
        super().closeEvent(event)

class ScreenerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Screener 2025")
        self.setGeometry(100, 100, 1200, 700)
        self.setStyleSheet("background-color: #0e0f15; color: #ffffff;")

        self.on_enter_options = lambda event: on_enter_options(self, event)
        self.on_leave_options = lambda event: on_leave_options(self, event)
        self.on_click_options = lambda: on_click_options(self)
        self.on_enter_filter = lambda event: on_enter_filter(self, event)
        self.on_leave_filter = lambda event: on_leave_filter(self, event)
        self.on_click_filter = lambda: on_click_filter(self)

        self.cargar_datos = lambda: cargar_datos(self)
        self.aplicar_filtro = lambda filtros: aplicar_filtro(self, filtros)
        self.exportar_datos = lambda: exportar_datos(self)
        self.actualizar_estado = lambda: actualizar_estado(self)
        self.eliminar_seleccion = lambda: eliminar_seleccion(self)

        setup_ui(self)

    def abrir_menu_opciones(self):
        menu = QMenu(self)
        tickers_action = QAction("🔄 Actualizar Tickers", self)
        tickers_action.triggered.connect(self.actualizar_tickers)
        menu.addAction(tickers_action)
        volumen_action = QAction("🔄 Actualizar Volumen y Datos", self)
        volumen_action.triggered.connect(self.actualizar_volumen_datos)
        menu.addAction(volumen_action)
        datos_action = QAction("🏠 Datos Actuales", self)
        datos_action.triggered.connect(self.abrir_datos_actuales)
        menu.addAction(datos_action)
        export_action = QAction("💾 Exportar", self)
        export_action.triggered.connect(self.exportar_datos)
        menu.addAction(export_action)
        button = self.sender()
        menu.exec_(button.mapToGlobal(button.rect().bottomLeft()))

    def actualizar_tickers(self):
        self.status_bar.showMessage("Iniciando actualización de tickers...")
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.thread = QThread()
        self.worker = WorkerActualizarTickers()
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.signals.progress.connect(self.progress_bar.setValue)
        self.worker.signals.message.connect(self.status_bar.showMessage)
        self.worker.signals.finished.connect(self._actualizacion_completada)
        self.worker.signals.error.connect(self._mostrar_error)
        self.worker.signals.finished.connect(self.thread.quit)
        self.worker.signals.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()

    def actualizar_volumen_datos(self):
        self.status_bar.showMessage("Iniciando actualización de volumen y datos...")
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.thread = QThread()
        self.worker = WorkerActualizarVolumenDatos()
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.signals.progress.connect(self.progress_bar.setValue)
        self.worker.signals.message.connect(self.status_bar.showMessage)
        self.worker.signals.finished.connect(self._actualizacion_completada)
        self.worker.signals.error.connect(self._mostrar_error)
        self.worker.signals.finished.connect(self.thread.quit)
        self.worker.signals.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()

    def abrir_datos_actuales(self):
        self.datos_window = DatosActualesWindow(self)
        self.datos_window.show()

    def _actualizacion_completada(self):
        self.status_bar.showMessage("Actualización completada", 3000)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(100)
        self.cargar_datos()

    def _mostrar_error(self, error_msg):
        self.status_bar.showMessage(error_msg, 10000)
        print(error_msg)
        self.progress_bar.setVisible(False)
        self.timer.stop()

    def abrir_filtros(self):
        from .filters import FilterDialog
        dialog = FilterDialog(self)
        if dialog.exec_():
            filtros = dialog.obtener_filtros()
            self.aplicar_filtro(filtros)

    def closeEvent(self, event):
        self.timer.stop()
        self.table.guardar_tamanos()
        super().closeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ScreenerApp()
    window.show()
    sys.exit(app.exec_())