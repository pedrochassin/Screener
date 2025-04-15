from PyQt5.QtCore import QPropertyAnimation, QSize, QRect
from PyQt5.QtGui import QColor

def animate_button(app, button, start_size, end_size, y_offset_start, y_offset_end, duration, on_finished=None):
    animation = QPropertyAnimation(button, b"geometry", app)
    
    # Obtener la posición base original del botón (almacenada al inicio o calculada)
    if not hasattr(button, 'base_geometry'):
        button.base_geometry = button.geometry()
    
    base_x = button.base_geometry.x()
    base_y = button.base_geometry.y()

    # Geometría inicial: usa la posición base ajustada por el offset inicial
    start_geometry = QRect(
        base_x - (start_size.width() - 32) // 2,  # Centrado en x respecto al tamaño original (32)
        base_y + y_offset_start,                  # Posición y ajustada por el offset inicial
        start_size.width(),
        start_size.height()
    )
    
    # Geometría final: usa la posición base ajustada por el offset final
    end_geometry = QRect(
        base_x - (end_size.width() - 32) // 2,    # Centrado en x respecto al tamaño original (32)
        base_y + y_offset_end,                    # Posición y ajustada por el offset final
        end_size.width(),
        end_size.height()
    )
    
    animation.setStartValue(start_geometry)
    animation.setEndValue(end_geometry)
    animation.setDuration(duration)
    if on_finished:
        animation.finished.connect(on_finished)
    animation.start()

def animate_border_color(app, button, start_color, end_color, duration):
    animation = QPropertyAnimation(button, b"borderColor", app)
    animation.setStartValue(start_color)
    animation.setEndValue(end_color)
    animation.setDuration(duration)
    animation.valueChanged.connect(lambda color: update_border_color(button, color))
    animation.start()

def update_border_color(button, color):
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

def on_enter_options(self, event):
    # Se agranda de 32x32 a 40x40 y se levanta 5 píxeles
    animate_button(self, self.options_button, QSize(32, 32), QSize(40, 40), 0, -5, 200)
    animate_border_color(self, self.options_button, QColor("#efd700"), QColor("#63b8ff"), 200)

def on_leave_options(self, event):
    # Vuelve de 40x40 a 32x32 y regresa a la posición original (y_offset = 0)
    animate_button(self, self.options_button, QSize(40, 40), QSize(32, 32), -5, 0, 200)
    animate_border_color(self, self.options_button, QColor("#63b8ff"), QColor("#0e0f15"), 200)

def on_click_options(self):
    # Animación de clic: se reduce a 28x28 y vuelve a 32x32 sin moverse en y
    animate_button(self, self.options_button, QSize(32, 32), QSize(28, 28), 0, 0, 100, 
                   lambda: animate_button(self, self.options_button, QSize(28, 28), QSize(32, 32), 0, 0, 100))

def on_enter_filter(self, event):
    # Se agranda de 32x32 a 40x40 y se levanta 5 píxeles
    animate_button(self, self.filter_button, QSize(32, 32), QSize(40, 40), 0, -5, 200)
    animate_border_color(self, self.filter_button, QColor("#63b8ff"), QColor("#efd700"), 200)

def on_leave_filter(self, event):
    # Vuelve de 40x40 a 32x32 y regresa a la posición original (y_offset = 0)
    animate_button(self, self.filter_button, QSize(40, 40), QSize(32, 32), -5, 0, 200)
    animate_border_color(self, self.filter_button, QColor("#efd700"), QColor("#0e0f15"), 200)

def on_click_filter(self):
    # Animación de clic: se reduce a 28x28 y vuelve a 32x32 sin moverse en y
    animate_button(self, self.filter_button, QSize(32, 32), QSize(28, 28), 0, 0, 100, 
                   lambda: animate_button(self, self.filter_button, QSize(28, 28), QSize(32, 32), 0, 0, 100))