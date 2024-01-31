
import cv2 as cv
import numpy as np
import pydicom as PDCM
import json
from PyQt6.QtWidgets import *
from PyQt6.QtGui import QPixmap, QPainter, QPen, QColor, QAction
from PyQt6.QtCore import Qt



def Dicom_to_Image(Path): #Montagem da imagem dicom
    DCM_Img = PDCM.read_file(Path)

    

    rows = DCM_Img.get(0x00280010).value 
    cols = DCM_Img.get(0x00280011).value 

    Instance_Number = int(DCM_Img.get(0x00200013).value) 
    Window_Center = int(DCM_Img.get(0x00281050).value) 
    Window_Width = int(DCM_Img.get(0x00281051).value) 

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

            if (Rescale_Pix_Val > Window_Max): 
                New_Img[i][j] = 255
            elif (Rescale_Pix_Val < Window_Min):
                New_Img[i][j] = 0 
            else:
                New_Img[i][j] = int(((Rescale_Pix_Val - Window_Min) / (Window_Max - Window_Min)) * 255) 
    Instance_Number=1
    return New_Img, Instance_Number


class MainWindow(QMainWindow): # Janela de edição de foto
    
    def __init__(self):
        super().__init__()


        self.setWindowTitle("ProgramaIC")

        self.previousPoint = None

        self.initialpositionX = None
        self.initialpositionY = None
        
        self.count = 0
       
        self.label = QLabel()
        img = QPixmap('./0000.jpg')
        
        img2 = img.scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        #Spacebar
        self.canvas= QPixmap(img)

        self.pen = QPen()
    
        self.pen.setWidth(2)
        self.pen.setColor(QColor("black"))
        self.pen.setCapStyle(Qt.PenCapStyle.RoundCap)

        self.label.setPixmap(self.canvas)
        self.setCentralWidget(self.label)

        self.lee = QLineEdit("", self)
        self.lee.setGeometry(0,28,100,20)
        self.lee.setStyleSheet('border-radius:4px; border-style:solid; border-width:1px; border-color:green; color:green; background-color:transparent;')

        toolbar=QToolBar("Toolbar")
        self.addToolBar(toolbar)
        colorAction = QAction("Escolha a cor", self)
        colorAction.triggered.connect(self.changeColor)

        saveAction = QAction("Salvar", self)
        saveAction.triggered.connect(self.saveToFile)

        toolbar.addAction(colorAction)
        toolbar.addAction(saveAction)
    
    def saveToFile(self):
        dialog = QFileDialog()
        dialog.setNameFilter("*.jpg")
        dialog.setDefaultSuffix(".jpg")
        clickedOK = dialog.exec()

        if clickedOK:
            self.canvas.save(dialog.selectedFiles()[0])

    def changeColor(self):
        dialog = QColorDialog()
        clickedOK = dialog.exec()

        if clickedOK:
            self.pen.setColor(dialog.currentColor())

    

    def mouseMoveEvent(self, event):
        position = event.pos()
        
        if self.initialpositionX == None:
            self.initialpositionX = position.x()
            self.initialpositionY = position.y()

        

        painter = QPainter(self.canvas)
        painter.setPen(self.pen)
        if self.previousPoint: painter.drawLine(self.previousPoint.x(), self.previousPoint.y()-25, position.x(), position.y()-25)
        else: painter.drawPoint(position.x(), position.y()-25)
        
        painter.end()

        self.previousPoint = position
        self.label.setPixmap(self.canvas)
    
    def mouseReleaseEvent(self, event):
        
        position = event.pos()
        painter = QPainter(self.canvas)

        self.lastpositionX = position.x()
        self.lastpositionY = position.y()

        
        painter.drawText(position.x(), position.y()-25, self.lee.text())
        painter.end()

        dicionario={
            "posicao_inicialX": self.initialpositionX,
            "posicao_inicialY": self.initialpositionY,
            "posicao_finalX": self.lastpositionX,
            "posicao_finalY": self.lastpositionY,
            "anotacao": self.lee.text(),
            "nome_paciente": "Alan"
        }
        object_json = json.dumps(dicionario, indent= 4)
        with open(f"imagem{valor_lido}.{doenca2}.{self.count}", "w") as file:
            file.write(object_json)

        self.lee.setText(None)

        self.previousPoint = position
        self.label.setPixmap(self.canvas)

        
        
        # painter = event.pos()
        # painter = QPainter(self.canvas)
        # painter.drawText
        self.previousPoint = None
        self.initialpositionY = None
        self.initialpositionX = None
        self.lastpositionX = None
        self.lastpositionY = None
        self.count = self.count+1

def main():
    
    def func4():
        doenca = le.text()
        global valor_lido
        valor_lido = li.text()

        global doenca2
        
        doenca2=doenca.upper()
        if doenca2 == "COVID":
            input_Image = (f"./HCFMRPCOVID_19_&_LID (v1)/3-COVID/covid-dcm-anonymized/{valor_lido}.dcm")
        elif doenca == "LID":
            input_Image = (f"./HCFMRPCOVID_19_&_LID (v1)/2-LID/lid-dcm-anonymized/{valor_lido}.dcm")
        else:
            input_Image = (f"./HCFMRPCOVID_19_&_LID (v1)/1-Normal/normal-dcm-anonymized/{valor_lido}.dcm")
        return input_Image
    
    
    
    app1=QApplication([])
    window2=QWidget()
    window2.resize(550,550)
    window2.setStyleSheet("background-color: #2D033B")

    def on_button_pressed():
        btn.setStyleSheet('color: black; background-color: #C147E9; border-radius: 4px')

    def on_button_released():
        btn.setStyleSheet('color: white; background-color: #810CA8; border-radius: 4px')

    btn = QPushButton("PESQUISAR", window2)
    btn.setGeometry(200,440,150,40)
    btn.setStyleSheet('color: white; background-color:#810CA8; border-radius:4px')

    btn.pressed.connect(on_button_pressed)
    btn.released.connect(on_button_released)
    btn.clicked.connect(func4)

    texto = QLabel("", window2)
    texto.setText("Qual é a doença?\n(COVID, LID ou sem doença)")
    texto.setGeometry(200, 30, 300, 100)
    texto.setStyleSheet('color: white')
    
    le=QLineEdit("",window2)
    le.setGeometry(200,110,150,40)
    le.setStyleSheet('border-radius:4px; background-color:#810CA8;')

    texto2 = QLabel("", window2)
    texto2.setText("Número da imagem desejada.")
    texto2.setGeometry(200, 205, 500, 100)
    texto2.setStyleSheet('color: white')

    li=QLineEdit("",window2)
    li.setGeometry(200,275,150,40)
    li.setStyleSheet('border-radius:4px; background-color:#810CA8;')

    window2.show()
    app1.exec()
    Input_Image = func4()
    ds=PDCM.dcmread(Input_Image)
    global patientname
    patientname = ds['PatientName']


    Output_Image, Instance_Number = Dicom_to_Image(Input_Image)

    cv.imwrite(str(Instance_Number - 1).zfill(4) + '.jpg', Output_Image)
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()  


if __name__ == "__main__":
    main()