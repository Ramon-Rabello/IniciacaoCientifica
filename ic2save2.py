
import cv2 as cv
import numpy as np
import pydicom as PDCM
import json
import os
from PIL import Image
from PyQt6.QtWidgets import *
from PyQt6.QtGui import QPixmap, QPainter, QPen, QColor, QAction, QIcon
from PyQt6.QtCore import Qt, QSize



def Dicom_to_Image(selected_image): #Montagem da imagem dicom
    im = PDCM.dcmread(selected_image)

    im = im.pixel_array.astype(float)

    rescaled_image = (np.maximum(im,0)/im.max())*255

    New_Img = np.uint8(rescaled_image)
    
    New_Img = Image.fromarray(New_Img)

    Instance_Number = 1

    max_size = (500, 800)
    New_Img.thumbnail(max_size, Image.LANCZOS)

    New_Img.save('0000.jpg')
    
    
    return New_Img, Instance_Number


class MainWindow(QMainWindow): # Janela de edição de foto
    
    def __init__(self):
        super().__init__()




        self.setWindowTitle("ProgramaIC")
        self.setStyleSheet("""
            QMainWindow {
                background-color: #333;
            }
            QLabel {
                color: #fff;
            }
            QPushButton {
                background-color: #555;
                color: #fff;
                border: none;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #777;
            }
            QLineEdit {
                background-color: #555;
                color: #fff;
                border: none;
                padding: 5px;
            }
            QToolBar {
                background-color: white;
            }
            QMenuBar {
                background-color: #333;
            }
        """)

        self.window_width = self.width()
        self.window_height = self.height()
        self.resize(700, self.height())

        self.previousPoint = None
        self.initialpositionX = None
        self.initialpositionY = None
        self.pixmap_stack = []
        self.image_files = []
        self.current_image_index = 0
        self.load_image_list()
        self.count = 0

        self.label = QLabel()
        self.label.setMouseTracking(True)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed) 

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        grid_layout = QGridLayout()
        central_widget.setLayout(grid_layout)

        # Botão Previous
        btnPrevious = QPushButton("", self)
        icon = QIcon("Icons/pngwing.com.png")
        btnPrevious.setIcon(icon)
        btnPrevious.setIconSize(QSize(50, 50))
        btnPrevious.setFlat(True)
        btnPrevious.setStyleSheet('color: white; background-color:#810CA8; border-radius:4px')
        btnPrevious.clicked.connect(self.btnPreviousPressed)
        btnPrevious.setFixedSize(50,  50)
        grid_layout.addWidget(btnPrevious, 0, 0)

        # Etiqueta para exibir a imagem
        grid_layout.addWidget(self.label, 0, 1)

        # Botão Next
        btnNext = QPushButton("", self)
        icon2 = QIcon("Icons/pngwing.com.png")
        btnNext.setIcon(icon2)
        btnNext.setIconSize(QSize(50, 50))
        btnNext.setFlat(True)
        btnNext.setStyleSheet('color: white; background-color:#810CA8; border-radius:4px')
        btnNext.clicked.connect(self.btnNextPressed)
        btnNext.setFixedSize(50,  50)
        grid_layout.addWidget(btnNext, 0, 2)

        

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

        img = QPixmap('./0000.jpg')
        
        img2 = img.scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        #Spacebar
        self.canvas = QPixmap(img)

        self.pen = QPen()
    
        self.pen.setWidth(2)
        self.pen.setColor(QColor("black"))
        self.pen.setCapStyle(Qt.PenCapStyle.RoundCap)

        self.label.setPixmap(self.canvas)

        self.label.setFixedSize(self.canvas.size()) 

        grid_layout.addWidget(self.label,  0,  1)
        # self.setCentralWidget(self.label)

    def load_image_list(self):
        # Caminho da pasta onde as imagens estão armazenadas
        folder_path = 'Sequence_Output'
        # Obtenha todos os arquivos .jpg na pasta
        self.image_files = [f for f in os.listdir(folder_path) if f.endswith('.png')]
        # Ordene a lista de arquivos por nome
        self.image_files.sort()

    def btnPreviousPressed(self):
        # Decrementa o índice da imagem atual
        self.current_image_index -= 1
        # Garanta que o índice não fique negativo
        if self.current_image_index < 0:
            self.current_image_index = 0
        # Carrega a imagem anterior
        self.load_image(self.current_image_index)
    
    def load_image(self, index):
        # Caminho da pasta onde as imagens estão armazenadas
        folder_path = 'Sequence_Output'
        # Nome do arquivo de imagem
        image_file = self.image_files[index]
        # Caminho completo do arquivo de imagem
        image_path = os.path.join(folder_path, image_file)
        # Carrega a imagem e define como QPixmap
        self.canvas = QPixmap(image_path)
        # Atualiza a label com a nova imagem
        self.label.setFixedSize(self.canvas.size()) 
        self.label.setPixmap(self.canvas)
    
    

    def btnNextPressed(self):
        # Incrementa o índice da imagem atual
        self.current_image_index += 1
        # Verifica se o índice não excede o número total de imagens
        if self.current_image_index >= len(self.image_files):
            self.current_image_index = len(self.image_files) - 1
        # Carrega a próxima imagem
        self.load_image(self.current_image_index)
        
    

    
    
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

    

    def mousePressEvent(self, event):
        position = self.label.mapFromGlobal(event.globalPosition().toPoint())
        self.initialpositionX = position.x()
        self.initialpositionY = position.y()
        self.previousPoint = position

    def mouseMoveEvent(self, event):
        position = self.label.mapFromGlobal(event.globalPosition().toPoint())
        
        if self.initialpositionX == None:
            self.initialpositionX = position.x()
            self.initialpositionY = position.y()

        

        painter = QPainter(self.canvas)
        painter.setPen(self.pen)
        if self.previousPoint: painter.drawLine(self.previousPoint.x(), self.previousPoint.y(), position.x(), position.y())
        else: painter.drawPoint(position.x(), position.y())
        
        painter.end()

        self.previousPoint = position
        self.label.setPixmap(self.canvas)
    
    def mouseReleaseEvent(self, event):
        position = self.label.mapFromGlobal(event.globalPosition().toPoint())
    
        painter = QPainter(self.canvas)

        self.lastpositionX = position.x()
        self.lastpositionY = position.y()

        painter.setPen(QColor("yellow"))
        painter.drawText(position.x(), position.y(), self.lee.text())
        painter.end()

        dicionario={
            "posicao_inicialX": self.initialpositionX,
            "posicao_inicialY": self.initialpositionY,
            "posicao_finalX": self.lastpositionX,
            "posicao_finalY": self.lastpositionY,
            "anotacao": self.lee.text()
        }
        object_json = json.dumps(dicionario, indent= 4)
        with open(f"Sequence_json/imagem43242{self.count}", "w") as file:
            file.write(object_json)

        self.lee.setText(None)

        self.pixmap_stack.append(self.canvas.copy()) #save copy

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
        # Abrir o diálogo para selecionar a imagem
        
        dialog = QFileDialog()
        dialog.setNameFilter("Images (*.dcm)")
        
        if dialog.exec():
            selected_image = dialog.selectedFiles()[0]
            # Retornar o caminho da imagem selecionada para a função func4
            Dicom_to_Image(selected_image)
            window2.close()
        else:
            print("Seleção de imagem cancelada pelo usuário.")
            return None
        
    
    
    
    app2=QApplication([])
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
    app2.exec()
    # Input_Image = func4()
    
    # ds=PDCM.dcmread(Input_Image)

    # global patientname
    # patientname = ds['PatientName']


    

    # cv.imwrite(str(Instance_Number - 1).zfill(4) + '.jpg', Output_Image)
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()  


if __name__ == "__main__":
    main()