from PyQt5.QtWidgets import QMainWindow, QAction, QMenu, QApplication
from PyQt5.QtCore import QThread
import sys
from .workers import WorkerSignals, WorkerActualizarTickers, WorkerActualizarVolumenDatos
from .ui_components import setup_ui
from .animations import (on_enter_options, on_leave_options, on_click_options,
                        on_enter_filter, on_leave_filter, on_click_filter)
from .data_handlers import (cargar_datos, aplicar_filtro, exportar_datos,
                           actualizar_estado, eliminar_seleccion)

class ScreenerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Screener 2025")
        self.setGeometry(100, 100, 1200, 700)
        self.setStyleSheet("background-color: #0e0f15; color: #ffffff;")

        # Asignar funciones de animación como métodos vinculados a la instancia
        self.on_enter_options = lambda event: on_enter_options(self, event)
        self.on_leave_options = lambda event: on_leave_options(self, event)
        self.on_click_options = lambda: on_click_options(self)
        self.on_enter_filter = lambda event: on_enter_filter(self, event)
        self.on_leave_filter = lambda event: on_leave_filter(self, event)
        self.on_click_filter = lambda: on_click_filter(self)

        # Asignar funciones de manejo de datos como métodos
        self.cargar_datos = lambda: cargar_datos(self)
        self.aplicar_filtro = lambda filtros: aplicar_filtro(self, filtros)
        self.exportar_datos = lambda: exportar_datos(self)
        self.actualizar_estado = lambda: actualizar_estado(self)
        self.eliminar_seleccion = lambda: eliminar_seleccion(self)

        # Configurar la interfaz gráfica
        setup_ui(self)

    def abrir_menu_opciones(self):
        menu = QMenu(self)
        # Botón para actualizar tickers
        tickers_action = QAction("🔄 Actualizar Tickers", self)
        tickers_action.triggered.connect(self.actualizar_tickers)
        menu.addAction(tickers_action)
        # Botón para actualizar volumen y datos
        volumen_action = QAction("🔄 Actualizar Volumen y Datos", self)
        volumen_action.triggered.connect(self.actualizar_volumen_datos)
        menu.addAction(volumen_action)
        # Botón de exportar (sin cambios)
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

    def _actualizacion_completada(self):
        self.status_bar.showMessage("Actualización completada", 3000)
        self.progress_bar.setValue(100)
        self.progress_bar.setVisible(False)
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