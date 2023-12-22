from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QToolBar, QColorDialog, QFileDialog
from PyQt6.QtGui import QPixmap, QPainter, QPen, QColor, QAction, QBrush
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import *

class MainWindow(QMainWindow):
    
    def __init__(self):
        super().__init__()


        self.setWindowTitle("Drawing App")

        self.previousPoint = None
       
        self.label = QLabel()
        img = QPixmap('./HCFMRPCOVID_19_&_LID (v1)/1-Normal/normal-png/1.png')
        img2 = img.scaled(1280, 720)
        self.canvas= QPixmap(img2)
        

        

        # label = QLabel(self)
        # pixmap = QPixmap()
        # label.setPixmap(pixmap)
        

        self.pen = QPen()
        self.pen.setWidth(3)
        self.pen.setColor(QColor("red"))
        self.pen.setCapStyle(Qt.PenCapStyle.RoundCap)

        self.label.setPixmap(self.canvas)
        self.setCentralWidget(self.label)

        

        btn = QPushButton("botão1", self)
        btn.setGeometry(0,0,150,80)
        btn.setStyleSheet('color: black; background-color:gray')
        btn.clicked.connect(self.criabox)

        self.userTextBox = QLineEdit("",self)
        self.userTextBox.setGeometry(100,100,100,100)

        self.userTextBox.setStyleSheet("""
            color: 'black';
            font-size:30px;
            border: 2px solid '#000000';
            min-width: 40px;
            min-height: 10px;
            background-color: blue;
            


                """)
        self.scene = QGraphicsScene(self)
        self.view = QGraphicsView(self.scene, self)

        self.textbox = QLineEdit()
        self.textbox.setText("Texto inicial")
        self.textbox.setGeometry(10, 10, 100, 30)

        self.proxy = self.scene.addWidget(self.textbox)
        self.proxy.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
    

    def criabox(self):
        self.userTextBox = QLineEdit("",self)
        self.userTextBox.setGeometry(100,100,100,100)

        self.userTextBox.setStyleSheet("""
            color: 'black';
            font-size:30px;
            border: 2px solid '#000000';
            min-width: 40px;
            min-height: 10px;
            background-color: black;
            


                """)



    def mouseMoveEvent(self, event):
        position = event.pos()

        painter = QPainter(self.canvas)
        painter.setPen(self.pen)
        if self.previousPoint: painter.drawLine(self.previousPoint.x(), self.previousPoint.y(), position.x(), position.y())
        else: painter.drawPoint(position.x(), position.y())
        
        painter.end()

        self.previousPoint = position
        self.label.setPixmap(self.canvas)
    
    def mouseReleaseEvent(self, event):
        self.previousPoint = None

    


app = QApplication([])
window = MainWindow()
window.show()
app.exec()  