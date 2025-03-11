import csv
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QTextBrowser, QPushButton
from PyQt5.QtCore import Qt
import re
import webbrowser
import html

def export_to_csv(table):
    """Exporta los datos de la tabla a un archivo CSV."""
    with open('screener_export.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        headers = [table.horizontalHeaderItem(col).text() for col in range(table.columnCount())]
        writer.writerow(headers)
        for row in range(table.rowCount()):
            row_data = [table.item(row, col).text() if table.item(row, col) else "" for col in range(table.columnCount())]
            writer.writerow(row_data)

def show_news(table):
    """Muestra una ventana con la noticia seleccionada, convirtiendo URLs en enlaces clicables."""
    selected = table.selectedItems()
    if not selected:
        return

    noticia = table.item(selected[0].row(), 7).text()  # Columna 7 es "Noticia"
    dialog = QDialog(table)
    dialog.setWindowTitle("Noticia")
    dialog.setMinimumWidth(400)
    dialog.setStyleSheet("background-color: #2a2a2a; color: #ffffff;")

    layout = QVBoxLayout(dialog)

    # Usamos QTextBrowser para mostrar texto con enlaces clicables
    news_display = QTextBrowser()
    news_display.setStyleSheet("background-color: #3a3a3a; color: #ffffff; border: none;")
    news_display.setOpenExternalLinks(True)  # Permite abrir enlaces en el navegador

    # Escapamos el texto original para manejar caracteres especiales
    noticia_escapada = html.escape(noticia)
    # Detectar URLs y convertirlas a enlaces HTML
    url_pattern = r'(https?://[^\s]+)'
    formatted_text = re.sub(url_pattern, r'<a href="\1" style="color: #1e90ff;">\1</a>', noticia_escapada)
    news_display.setHtml(formatted_text)  # Establece el texto como HTML

    layout.addWidget(news_display)

    close_btn = QPushButton("Cerrar")
    close_btn.setStyleSheet("background-color: #4a4a4a; color: #ffffff; padding: 5px;")
    close_btn.clicked.connect(dialog.accept)
    layout.addWidget(close_btn, alignment=Qt.AlignRight)

    dialog.exec_()