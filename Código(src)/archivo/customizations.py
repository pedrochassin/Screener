from PyQt5.QtWidgets import QGraphicsDropShadowEffect, QGraphicsOpacityEffect, QShortcut, QTableWidget
from PyQt5.QtCore import QPropertyAnimation, QRect, QSize
from PyQt5.QtGui import QColor, QTransform, QIcon, QPixmap, QKeySequence
from PyQt5.QtMultimedia import QSound

class Customizations:
    def __init__(self, app):
        self.app = app  # Referencia a la instancia de ScreenerApp
        try:
            self.click_sound = QSound("C:/Users/Admin/Documents/Screener 2025/click.wav", self.app)  # Ajusta la ruta al archivo de sonido
            self.sound_available = True
        except Exception as e:
            print(f"Error al cargar el archivo de sonido: {e}")
            self.sound_available = False

    def apply_visual_customizations(self):
        # Fondo con gradiente
        self.app.setStyleSheet("background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #0e0f15, stop:1 #1a1c2c); color: #ffffff;")

        # Sombras y esquinas redondeadas para los botones
        shadow = QGraphicsDropShadowEffect(self.app)
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 160))
        shadow.setOffset(2, 2)
        self.app.options_button.setGraphicsEffect(shadow)

        shadow = QGraphicsDropShadowEffect(self.app)
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 160))
        shadow.setOffset(2, 2)
        self.app.filter_button.setGraphicsEffect(shadow)

        # Estilo con esquinas redondeadas y tooltips personalizados
        self.app.options_button.setStyleSheet("""
            QPushButton { 
                background-color: #0e0f15; 
                border: 1px solid #0e0f15; 
                padding: 2px; 
                border-radius: 5px; 
            }
            QPushButton:hover { 
                background-color: #4a4a4a; 
            }
            QToolTip { 
                background-color: #2a2a2a; 
                color: #ffffff; 
                border: 1px solid #63b8ff; 
                padding: 2px; 
            }
        """)
        self.app.filter_button.setStyleSheet("""
            QPushButton { 
                background-color: #0e0f15; 
                border: 1px solid #1e90ff; 
                padding: 2px; 
                border-radius: 5px; 
            }
            QPushButton:hover { 
                background-color: #4a4a4a; 
                border: 1px solid #63b8ff; 
            }
            QToolTip { 
                background-color: #2a2a2a; 
                color: #ffffff; 
                border: 1px solid #63b8ff; 
                padding: 2px; 
            }
        """)

        # Tooltips
        self.app.options_button.setToolTip("Opciones: Actualizar o Exportar datos")
        self.app.filter_button.setToolTip("Filtrar datos de la tabla")

        # Estilo de la tabla para resaltar filas al pasar el mouse
        self.app.table.setStyleSheet("""
            QTableWidget {
                background-color: #1a1c2c;
                color: #ffffff;
            }
            QTableWidget::item:hover {
                background-color: #2a2c3c;
            }
            QTableWidget::item:selected {
                background-color: #63b8ff;
            }
        """)

    def apply_shortcuts(self):
        # Atajos de teclado
        shortcut_options = QShortcut(QKeySequence("Ctrl+O"), self.app)
        shortcut_options.activated.connect(self.app.abrir_menu_opciones)

        shortcut_filter = QShortcut(QKeySequence("Ctrl+F"), self.app)
        shortcut_filter.activated.connect(self.app.abrir_filtros)

    def toggle_theme(self):
        if self.app.styleSheet().startswith("background: qlineargradient"):
            # Cambiar a tema claro
            self.app.setStyleSheet("background-color: #f0f0f0; color: #000000;")
            self.app.status_bar.setStyleSheet("background-color: #d0d0d0; color: #000000;")
            self.app.options_button.setStyleSheet("""
                QPushButton { 
                    background-color: #f0f0f0; 
                    border: 1px solid #000000; 
                    padding: 2px; 
                    border-radius: 5px; 
                }
                QPushButton:hover { 
                    background-color: #d0d0d0; 
                }
                QToolTip { 
                    background-color: #2a2a2a; 
                    color: #ffffff; 
                    border: 1px solid #63b8ff; 
                    padding: 2px; 
                }
            """)
            self.app.filter_button.setStyleSheet("""
                QPushButton { 
                    background-color: #f0f0f0; 
                    border: 1px solid #000000; 
                    padding: 2px; 
                    border-radius: 5px; 
                }
                QPushButton:hover { 
                    background-color: #d0d0d0; 
                    border: 1px solid #333333; 
                }
                QToolTip { 
                    background-color: #2a2a2a; 
                    color: #ffffff; 
                    border: 1px solid #63b8ff; 
                    padding: 2px; 
                }
            """)
            self.app.table.setStyleSheet("""
                QTableWidget {
                    background-color: #e0e0e0;
                    color: #000000;
                }
                QTableWidget::item:hover {
                    background-color: #c0c0c0;
                }
                QTableWidget::item:selected {
                    background-color: #63b8ff;
                }
            """)
        else:
            # Volver a tema oscuro
            self.app.setStyleSheet("background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #0e0f15, stop:1 #1a1c2c); color: #ffffff;")
            self.app.status_bar.setStyleSheet("background-color: #0e0f15; color: #ffffff;")
            self.app.options_button.setStyleSheet("""
                QPushButton { 
                    background-color: #0e0f15; 
                    border: 1px solid #0e0f15; 
                    padding: 2px; 
                    border-radius: 5px; 
                }
                QPushButton:hover { 
                    background-color: #4a4a4a; 
                }
                QToolTip { 
                    background-color: #2a2a2a; 
                    color: #ffffff; 
                    border: 1px solid #63b8ff; 
                    padding: 2px; 
                }
            """)
            self.app.filter_button.setStyleSheet("""
                QPushButton { 
                    background-color: #0e0f15; 
                    border: 1px solid #1e90ff; 
                    padding: 2px; 
                    border-radius: 5px; 
                }
                QPushButton:hover { 
                    background-color: #4a4a4a; 
                    border: 1px solid #63b8ff; 
                }
                QToolTip { 
                    background-color: #2a2a2a; 
                    color: #ffffff; 
                    border: 1px solid #63b8ff; 
                    padding: 2px; 
                }
            """)
            self.app.table.setStyleSheet("""
                QTableWidget {
                    background-color: #1a1c2c;
                    color: #ffffff;
                }
                QTableWidget::item:hover {
                    background-color: #2a2c3c;
                }
                QTableWidget::item:selected {
                    background-color: #63b8ff;
                }
            """)

    def animate_button(self, button, start_size, end_size, duration, on_finished=None):
        animation = QPropertyAnimation(button, b"geometry", self.app)
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
        animation = QPropertyAnimation(button, b"borderColor", self.app)
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
                border-radius: 5px; 
            }}
            QPushButton:hover {{ 
                background-color: #ffc600; 
            }}
            QToolTip {{ 
                background-color: #2a2a2a; 
                color: #ffffff; 
                border: 1px solid #63b8ff; 
                padding: 2px; 
            }}
        """)

    def animate_opacity(self, widget, start_opacity, end_opacity, duration):
        opacity_effect = QGraphicsOpacityEffect(widget)
        widget.setGraphicsEffect(opacity_effect)
        animation = QPropertyAnimation(opacity_effect, b"opacity", self.app)
        animation.setStartValue(start_opacity)
        animation.setEndValue(end_opacity)
        animation.setDuration(duration)
        animation.start()

    def animate_rotation(self, button, start_angle, end_angle, duration, icon_path):
        animation = QPropertyAnimation(button, b"rotation", self.app)
        animation.setStartValue(start_angle)
        animation.setEndValue(end_angle)
        animation.setDuration(duration)
        animation.valueChanged.connect(lambda angle: button.setIcon(QIcon(QPixmap(icon_path).transformed(QTransform().rotate(angle)))))
        animation.start()

    def play_click_sound(self):
        if self.sound_available:
            self.click_sound.play()

    def animate_table_load(self, table):
        opacity_effect = QGraphicsOpacityEffect(table)
        table.setGraphicsEffect(opacity_effect)
        animation = QPropertyAnimation(opacity_effect, b"opacity", self.app)
        animation.setStartValue(0.0)
        animation.setEndValue(1.0)
        animation.setDuration(500)
        animation.start()