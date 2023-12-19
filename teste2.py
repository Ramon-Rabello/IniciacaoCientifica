from PyQt6.QtWidgets import *
from PyQt6.QtGui import QIcon, QFont, QPixmap, QMovie, QRegion
from PyQt6.QtCore import Qt
import sys

class Window(QWidget):
    def __init__(self):
        super().__init__()
 
        self.setGeometry(200, 200, 700, 400)
        self.setWindowTitle("Python QLabel")
        self.setWindowIcon(QIcon('qt.png'))
 
 
        label = QLabel(self)
        pixmap = QPixmap('./img/imagem_teste.png')
        label.setPixmap(pixmap)
 
 
 
app = QApplication(sys.argv)
window = Window()
window.show()
sys.exit(app.exec())