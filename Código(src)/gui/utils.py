from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QTextEdit, QFileDialog, QMessageBox
from PyQt5.QtCore import Qt
import csv

def export_to_csv(table):
    filepath, _ = QFileDialog.getSaveFileName(None, "Guardar como CSV", "", "CSV Files (*.csv)")
    if filepath:
        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Fecha", "Ticker", "Precio", "Cambio %", "Volumen", "Categoría", "Noticia"])
            for row in range(table.rowCount()):
                row_data = [table.item(row, col).text() for col in range(table.columnCount())]
                writer.writerow(row_data)
        QMessageBox.information(None, "Éxito", f"Datos exportados a {filepath}")

def show_news(table):
    selected = table.selectedItems()
    if selected:
        noticia = table.item(selected[0].row(), 6).text()
        dialog = QDialog()
        dialog.setWindowTitle("Noticia")
        dialog.setFixedSize(500, 300)
        dialog.setStyleSheet("background-color: #1e1e1e; color: #ffffff;")
        layout = QVBoxLayout(dialog)
        layout.addWidget(QLabel("Noticia", styleSheet="font: bold 12pt;"))
        text = QTextEdit()
        text.setReadOnly(True)
        text.setText(noticia)
        text.setStyleSheet("background-color: #2a2a2a;")
        layout.addWidget(text)
        dialog.exec_()
    else:
        QMessageBox.information(None, "Info", "Selecciona un ticker para ver su noticia.")