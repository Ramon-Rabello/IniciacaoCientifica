# This program is written by Abubakr Shafique (abubakr.shafique@gmail.com) 
import cv2 as cv
import numpy as np
import pydicom as PDCM
from PyQt6.QtWidgets import *
import matplotlib.pyplot as plt
import sys
from PyQt6.QtGui import QPixmap, QPainter, QPen, QColor, QAction, QBrush
from PyQt6.QtCore import QSize, Qt

def Dicom_to_Image(Path):
    DCM_Img = PDCM.read_file(Path)

    rows = DCM_Img.get(0x00280010).value #Get number of rows from tag (0028, 0010)
    cols = DCM_Img.get(0x00280011).value #Get number of cols from tag (0028, 0011)

    Instance_Number = int(DCM_Img.get(0x00200013).value) #Get actual slice instance number from tag (0020, 0013)

    Window_Center = int(DCM_Img.get(0x00281050).value) #Get window center from tag (0028, 1050)
    Window_Width = int(DCM_Img.get(0x00281051).value) #Get window width from tag (0028, 1051)

    Window_Max = int(Window_Center + Window_Width / 2)
    Window_Min = int(Window_Center - Window_Width / 2)

    if (DCM_Img.get(0x00281052) is None):
        Rescale_Intercept = 0
    else:
        Rescale_Intercept = int(DCM_Img.get(0x00281052).value)

    if (DCM_Img.get(0x00281053) is None):
        Rescale_Slope = 1
    else:
        Rescale_Slope = int(DCM_Img.get(0x00281053).value)

    New_Img = np.zeros((rows, cols), np.uint8)
    Pixels = DCM_Img.pixel_array

    for i in range(0, rows):
        for j in range(0, cols):
            Pix_Val = Pixels[i][j]
            Rescale_Pix_Val = Pix_Val * Rescale_Slope + Rescale_Intercept

            if (Rescale_Pix_Val > Window_Max): #if intensity is greater than max window
                New_Img[i][j] = 255
            elif (Rescale_Pix_Val < Window_Min): #if intensity is less than min window
                New_Img[i][j] = 0
            else:
                New_Img[i][j] = int(((Rescale_Pix_Val - Window_Min) / (Window_Max - Window_Min)) * 255) #Normalize the intensities
    Instance_Number=1
    return New_Img, Instance_Number



class MainWindow(QMainWindow):
    
    def __init__(self):
        super().__init__()


        self.setWindowTitle("Drawing App")

        self.previousPoint = None
       
        self.label = QLabel()
        img = QPixmap('./0000.jpg')
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

    




def main():
    Input_Image = './HCFMRPCOVID_19_&_LID (v1)/1-Normal/normal-dcm-anonymized/300.dcm'

    Output_Image, Instance_Number = Dicom_to_Image(Input_Image)

    cv.imwrite(str(Instance_Number - 1).zfill(4) + '.jpg', Output_Image)
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()  


    

if __name__ == "__main__":
    main()