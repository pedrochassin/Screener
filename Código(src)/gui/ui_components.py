from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QStatusBar, QProgressBar
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon, QPixmap
from .widgets import DataTable
from .table_customization import customize_table, apply_delegate, apply_custom_rounded

def setup_ui(app):
    central_widget = QWidget()
    app.setCentralWidget(central_widget)
    main_layout = QVBoxLayout(central_widget)
    main_layout.setContentsMargins(0, 0, 0, 0)
    main_layout.setSpacing(0)

    button_layout = QHBoxLayout()
    button_layout.setAlignment(Qt.AlignLeft)
    button_layout.setContentsMargins(5, 5, 0, 0)
    button_layout.setSpacing(5)

    # Botón de opciones
    pixmap_options = QPixmap("C:/Users/Admin/Documents/Screener 2025/Option_icon.png")
    if pixmap_options.isNull():
        print("Error: No se pudo cargar el ícono de Opciones. Verifica la ruta o el archivo.")
    else:
        pixmap_options = pixmap_options.scaled(24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        icon_options = QIcon(pixmap_options)
        app.options_button = QPushButton(app)
        app.options_button.setIcon(icon_options)
        app.options_button.setStyleSheet("""
            QPushButton { 
                background-color: #0e0f15; 
                border: 1px solid #0e0f15;
                padding: 2px; 
            }
            QPushButton:hover { 
                background-color: #4a4a4a; 
            }
        """)
        app.options_button.setFixedSize(32, 32)
        app.options_button.clicked.connect(app.abrir_menu_opciones)
        app.options_button.enterEvent = app.on_enter_options
        app.options_button.leaveEvent = app.on_leave_options
        app.options_button.clicked.connect(app.on_click_options)
        button_layout.addWidget(app.options_button)

    # Botón de filtros
    pixmap_filter = QPixmap("C:/Users/Admin/Documents/Screener 2025/Filter_icon.png")
    if pixmap_filter.isNull():
        print("Error: No se pudo cargar el ícono de Filtrar. Verifica la ruta o el archivo.")
    else:
        pixmap_filter = pixmap_filter.scaled(24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        icon_filter = QIcon(pixmap_filter)
        app.filter_button = QPushButton(app)
        app.filter_button.setIcon(icon_filter)
        app.filter_button.setStyleSheet("""
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
        app.filter_button.setFixedSize(32, 32)
        app.filter_button.clicked.connect(app.abrir_filtros)
        app.filter_button.enterEvent = app.on_enter_filter
        app.filter_button.leaveEvent = app.on_leave_filter
        app.filter_button.clicked.connect(app.on_click_filter)
        button_layout.addWidget(app.filter_button)

    main_layout.addLayout(button_layout)

    # Tabla
    app.table = DataTable(app)
    main_layout.addWidget(app.table)

    # Barra de estado
    app.status_bar = QStatusBar()
    app.status_bar.setStyleSheet("background-color: #0e0f15; color: #ffffff;")
    app.setStatusBar(app.status_bar)
    app.table.itemSelectionChanged.connect(app.actualizar_estado)

    # Barra de progreso
    app.progress_bar = QProgressBar(app)
    app.progress_bar.setStyleSheet("""
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
    app.progress_bar.setMaximumWidth(200)
    app.progress_bar.setVisible(False)
    app.status_bar.addPermanentWidget(app.progress_bar)

    # Timer
    app.timer = QTimer(app)
    app.timer.timeout.connect(app.cargar_datos)

    # Configuración inicial de la tabla
    app.cargar_datos()
    apply_delegate(app.table, rounded_columns=[2, 3, 4], text_color="#00f4cf", background_color="#0e2524")
    rounded_styles = {
        1: {'background_color': '#1d1c44', 'text_color': '#aeddf1'},
        13: {'background_color': '#3a2c18', 'text_color': '#fef399'}
    }
    apply_custom_rounded(app.table, rounded_styles)
    apply_delegate(app.table)