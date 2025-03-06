from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox, QHBoxLayout
from PyQt5.QtCore import Qt

class FilterDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("Filtrar Datos")
        self.setFixedSize(400, 400)
        self.setStyleSheet("background-color: #1e1e1e; color: #ffffff;")

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Filtrar por:"))

        # Ticker
        layout.addWidget(QLabel("Ticker:"))
        self.ticker_entry = QLineEdit()
        layout.addWidget(self.ticker_entry)

        # CambioPorcentaje
        layout.addWidget(QLabel("Cambio %:"))
        self.cambio_op = QComboBox()
        self.cambio_op.addItems([">", "<", "="])
        self.cambio_entry = QLineEdit()
        cambio_layout = QHBoxLayout()
        cambio_layout.addWidget(self.cambio_op)
        cambio_layout.addWidget(self.cambio_entry)
        layout.addLayout(cambio_layout)

        # Volumen
        layout.addWidget(QLabel("Volumen:"))
        self.volumen_op = QComboBox()
        self.volumen_op.addItems([">", "<", "="])
        self.volumen_entry = QLineEdit()
        volumen_layout = QHBoxLayout()
        volumen_layout.addWidget(self.volumen_op)
        volumen_layout.addWidget(self.volumen_entry)
        layout.addLayout(volumen_layout)

        # Categoría
        layout.addWidget(QLabel("Categoría:"))
        self.categoria_entry = QLineEdit()
        layout.addWidget(self.categoria_entry)

        # Botón Aplicar
        apply_btn = QPushButton("Aplicar Filtro")
        apply_btn.clicked.connect(self.accept)
        layout.addWidget(apply_btn)

    def obtener_filtros(self):
        return {
            "ticker": self.ticker_entry.text(),
            "cambio": self.cambio_entry.text(),
            "cambio_operador": self.cambio_op.currentText(),
            "volumen": self.volumen_entry.text(),
            "volumen_operador": self.volumen_op.currentText(),
            "categoria": self.categoria_entry.text()
        }