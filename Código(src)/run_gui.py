from PyQt5.QtWidgets import QApplication
import sys
from gui.app import ScreenerApp

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ScreenerApp()
    window.show()
    sys.exit(app.exec_())