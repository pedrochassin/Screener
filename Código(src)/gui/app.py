from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QMenuBar, QAction, QStatusBar, QMenu, QProgressBar, QStyledItemDelegate, QStyleOptionViewItem, QStyle, QTableWidgetItem
from PyQt5.QtCore import Qt, QObject, pyqtSignal, QTimer, QThread, QRect
from PyQt5.QtGui import QColor, QPainter, QBrush
from datetime import datetime
import threading
import traceback
import time
from .widgets import DataTable
from .filters import FilterDialog
from .utils import export_to_csv
from Base_Datos import conectar, leer_datos
from archivo.main import buscar_tickers
from scraper_yahoo import main as actualizar_volumen_y_datos

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

class RoundedRectDelegate(QStyledItemDelegate):
    def __init__(self, parent=None, date_column=0, target_columns=None):
        super().__init__(parent)
        self.date_column = date_column
        self.target_columns = target_columns if target_columns is not None else []

    def paint(self, painter, option, index):
        if index.column() in self.target_columns:
            table = self.parent()
            date_item = table.item(index.row(), self.date_column)
            hoy = datetime.now().strftime("%Y-%m-%d")
            if date_item and date_item.text() == hoy:
                painter.save()

                background_color = QColor("#0e2524")
                radius = 10

                painter.setRenderHint(QPainter.Antialiasing)
                brush = QBrush(background_color)
                painter.setBrush(brush)
                painter.setPen(Qt.NoPen)

                rect = QRect(option.rect.adjusted(2, 2, -2, -2))
                painter.drawRoundedRect(rect, radius, radius)

                painter.restore()

        option_copy = QStyleOptionViewItem(option)
        self.initStyleOption(option_copy, index)
        if index.column() in self.target_columns and date_item and date_item.text() == hoy:
            # Centrar el texto horizontalmente
            option_copy.textAlignment = Qt.AlignCenter
            option_copy.textAlignment = Qt.AlignCenter | Qt.AlignVCenter
            # Cambiar el color del texto
            option_copy.palette.setColor(option_copy.palette.Text, QColor("#00f4cf"))

        painter.save()
        self.parent().style().drawControl(QStyle.CE_ItemViewItem, option_copy, painter, self.parent())
        painter.restore()

class ScreenerApp(QMainWindow):
    def __init__(self): 
        super().__init__()
        self.setWindowTitle("Screener 2025")
        self.setGeometry(100, 100, 1200, 700)
        self.setStyleSheet("background-color: #0e0f15; color: #ffffff;")
    
        menubar = self.menuBar()
        menubar.setStyleSheet("""
            QMenuBar {
                background-color: #0e0f15;
                color: #ffffff;
            }
            QMenuBar::item {
                background-color: #0e0f15;
                padding: 5px 10px;
            }
            QMenuBar::item:selected {
                background-color: #4a4a4a;
                color: #ffffff;
                transition: background-color 0.3s ease;
            }
            QMenu {
                background-color: #0e0f15;
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
        self.max_updates = 5

        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.cargar_datos)
        self.refresh_timer.start(300000)

        self.cargar_datos()

        delegate = RoundedRectDelegate(self.table, date_column=0, target_columns=[2, 3, 4, 11, 18, 19])
        for col in [2, 3, 4, 11, 18, 19]:
            self.table.setItemDelegateForColumn(col, delegate)

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

                # Centrar los datos de ciertas columnas
                columnas_a_centrar = [2, 3, 4, 11, 18, 19]  # Índices de las columnas a centrar
                for row in range(self.table.rowCount()):
                    for col in columnas_a_centrar:
                        item = self.table.item(row, col)
                        if item:
                            item.setTextAlignment(Qt.AlignCenter)  # Centrar horizontal y verticalmente

                # Cambiar a negrita las columnas 1 y 5
                columnas_negrita = [1, 5]  # Índices de las columnas a poner en negrita
                for row in range(self.table.rowCount()):
                    for col in columnas_negrita:
                        item = self.table.item(row, col)
                        if item:
                            font = item.font()
                            font.setBold(True)  # Hacer el texto en negrita
                            item.setFont(font)
                        else:
                            # Si no hay un QTableWidgetItem, crea uno para la celda
                            item = QTableWidgetItem(self.table.item(row, col).text() if self.table.item(row, col) else "")
                            font = item.font()
                            font.setBold(True)
                            item.setFont(font)
                            self.table.setItem(row, col, item)
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