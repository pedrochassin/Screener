from PyQt5.QtCore import QObject, pyqtSignal
import time
import traceback
from archivo.main import buscar_tickers
from scraper_yahoo import main as actualizar_volumen_y_datos

class WorkerSignals(QObject):
    progress = pyqtSignal(int)
    message = pyqtSignal(str)
    finished = pyqtSignal()
    error = pyqtSignal(str)

class WorkerActualizarTickers(QObject):
    def __init__(self):
        super().__init__()
        self.signals = WorkerSignals()

    def run(self):
        try:
            self.signals.message.emit("Iniciando actualización de tickers...")
            self.signals.progress.emit(0)
            time.sleep(0.01)

            for i in range(0, 50, 2):
                self.signals.progress.emit(i)
                time.sleep(0.02)

            self.signals.message.emit("Actualizando tickers...")
            buscar_tickers()

            for i in range(50, 100, 2):
                self.signals.progress.emit(i)
                time.sleep(0.05)

            self.signals.message.emit("Actualización de tickers completada")
            self.signals.finished.emit()
        except Exception as e:
            error_msg = f"Error al actualizar tickers: {str(e)}\n{traceback.format_exc()}"
            self.signals.error.emit(error_msg)

class WorkerActualizarVolumenDatos(QObject):
    def __init__(self):
        super().__init__()
        self.signals = WorkerSignals()

    def run(self):
        try:
            self.signals.message.emit("Iniciando actualización de volumen y datos...")
            self.signals.progress.emit(0)
            time.sleep(0.01)

            for i in range(0, 50, 2):
                self.signals.progress.emit(i)
                time.sleep(0.02)

            self.signals.message.emit("Actualizando volumen y datos históricos...")
            actualizar_volumen_y_datos()

            for i in range(50, 100, 2):
                self.signals.progress.emit(i)
                time.sleep(0.05)

            self.signals.message.emit("Actualización de volumen y datos completada")
            self.signals.finished.emit()
        except Exception as e:
            error_msg = f"Error al actualizar volumen y datos: {str(e)}\n{traceback.format_exc()}"
            self.signals.error.emit(error_msg)