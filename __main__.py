import PyQt5
from PyQt5.QtWidgets import *

import sys

from home_ui import Ui_Home

class MainWindow(QMainWindow, Ui_Home):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.setupUi(self)

def main():
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
