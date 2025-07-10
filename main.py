import sys
from PyQt5.QtWidgets import QApplication
from map_board import MapBoard


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MapBoard()
    sys.exit(app.exec_())
