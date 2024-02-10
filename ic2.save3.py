
import cv2 as cv
import numpy as np
import pydicom as PDCM
import json
import os
from PIL import Image
from PIL.ImageQt import ImageQt
from PyQt6.QtWidgets import *

from PyQt6.QtGui import QPixmap, QPainter, QPen, QColor, QAction, QIcon, QShortcut, QKeySequence
from PyQt6.QtCore import Qt, QSize


annotations = []



def get_names(path):
    names = []
    for root, dirnames, filenames in os.walk(path):
        for filename in filenames:
            _, ext = os.path.splitext(filename)
            if ext in ['.dcm']:
                names.append(filename)
    return names

def convert_dcm_png(path,name):
    im = PDCM.dcmread(path + '/' + name)
    im = im.pixel_array.astype(float)
    rescaled_image = (np.maximum(im,   0) / im.max()) *   255
    New_Img = np.uint8(rescaled_image)
    New_Img = Image.fromarray(New_Img)
    # Converte a imagem PIL para QImage
    qimage = ImageQt(New_Img)
    # Converte QImage para QPixmap
    pixmap = QPixmap.fromImage(qimage)
    return pixmap


class MainWindow(QMainWindow): # Janela de edição de foto
    
    
    def __init__(self):
        super().__init__()
        self.Presscount = 0
        undoShortcut = QShortcut(QKeySequence("Ctrl+Z"), self)
        undoShortcut.activated.connect(self.undoLastChange)

        self.image_index_stack = []

        self.undo_stack = []
        self.undo_counter =  0

        self.temp_widget = QWidget()
        self.temp_widget.hide()


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
       
        # self.load_image_list()
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

        saveAnnotationsAction = QAction("Salvar Anotações", self)
        saveAnnotationsAction.triggered.connect(self.saveAllAnnotations)
        toolbar.addAction(saveAnnotationsAction)
        
        if len(image_array) % 2 != 0:
            self.current_image_index= ((len(image_array)+1)/2) -1
        else:
            self.current_image_index = (len(image_array)/2) -1

        self.current_image_index = int(self.current_image_index)

        img = QPixmap(image_array[self.current_image_index])
        
        # img2 = img.scaled(self.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        # #Spacebar
        self.canvas = QPixmap(img)
    
        self.pen = QPen()
    
        self.pen.setWidth(2)
        self.pen.setColor(QColor("black"))
        self.pen.setCapStyle(Qt.PenCapStyle.RoundCap)

        self.label.setPixmap(self.canvas)

        self.label.setFixedSize(self.canvas.size()) 

        grid_layout.addWidget(self.label,  0,  1)
        self.label.setPixmap(self.canvas)
            

    
    

    def saveAllAnnotations(self):
        # Abre uma caixa de diálogo para o usuário escolher o local e o nome do arquivo
        dialog = QFileDialog()
        dialog.setOption(QFileDialog.Option.DontUseNativeDialog)
        dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
        dialog.setNameFilter("JSON files (*.json)")
        dialog.setDefaultSuffix(".json")
        clickedOK = dialog.exec()

        if clickedOK:
            # Salva todas as anotações no arquivo JSON escolhido pelo usuário
            with open(dialog.selectedFiles()[0], "w") as file:
                json.dump(annotations, file, indent=4)

    def undoLastChange(self):
        
        if len(self.undo_stack) >  0:
            # Desempilhe o último pixmap e remova-o da pilha
            last_pixmap = self.undo_stack.pop()
            last_index = self.image_index_stack.pop()
            
            self.current_image_index = last_index
            image_array[self.current_image_index] = last_pixmap
            # Redefina o pixmap atual para o último pixmap desempilhado
            self.canvas = last_pixmap
            self.label.setPixmap(self.canvas)
            


        else:
            # Se não houver mais pixmaps na pilha, não faça nada
            pass
        # self.setCentralWidget(self.label)

    # def load_image_list(self):
    #     # Caminho da pasta onde as imagens estão armazenadas
    #     folder_path = 'Sequence_Output'
    #     # Obtenha todos os arquivos .jpg na pasta
    #     self.image_files = [f for f in os.listdir(folder_path) if f.endswith('.png')]
    #     # Ordene a lista de arquivos por nome
    #     self.image_files.sort()
    
    def btnPreviousPressed(self):
        if self.Presscount == 0:
            image_array[self.current_image_index] = self.canvas.copy()
            self.Presscount = 1
         # Decrementa o índice da imagem atual
        
        self.current_image_index -=  1
        # Garanta que o índice não fique negativo
        if self.current_image_index <  0:
            self.current_image_index =  0
        # Carrega a imagem anterior
        self.load_image(self.current_image_index)
    
    def load_image(self, index):

        # Usa o image_array em vez de ler do disco novamente
        self.canvas = image_array[index]

        # Atualiza a label com a nova imagem
        self.label.setFixedSize(self.canvas.size())  
        self.label.setPixmap(self.canvas)
    

    def btnNextPressed(self):
        if self.Presscount == 0:
            image_array[self.current_image_index] = self.canvas.copy()
            self.Presscount = 1

        # Incrementa o índice da imagem atual
        self.current_image_index +=  1
        # Verifica se o índice não excede o número total de imagens
        if self.current_image_index >= len(image_array):
            self.current_image_index = len(image_array) -  1
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
        self.undo_stack.append(self.canvas.copy())
        self.image_index_stack.append(self.current_image_index)
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
        
        if len(self.undo_stack) >  3:
            self.undo_stack.pop(0)


        position = self.label.mapFromGlobal(event.globalPosition().toPoint())
    
        painter = QPainter(self.canvas)

        self.lastpositionX = position.x()
        self.lastpositionY = position.y()

        painter.setPen(QColor("yellow"))
        painter.drawText(position.x(), position.y(), self.lee.text())
        painter.end()

        
        annotations.append({
            "numeracao": self.current_image_index +1,
            "posicao_inicialX": self.initialpositionX,
            "posicao_inicialY": self.initialpositionY,
            "posicao_finalX": self.lastpositionX,
            "posicao_finalY": self.lastpositionY,
            "anotacao": self.lee.text()
        })


        # dicionario={
        #     "posicao_inicialX": self.initialpositionX,
        #     "posicao_inicialY": self.initialpositionY,
        #     "posicao_finalX": self.lastpositionX,
        #     "posicao_finalY": self.lastpositionY,
        #     "anotacao": self.lee.text()
        # }
        # object_json = json.dumps(dicionario, indent= 4)
        # with open(f"Sequence_json/testeAqui{self.count}", "w") as file:
        #     file.write(object_json)

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

        self.lee.clearFocus()


def main():

    

    def func4():
        
        # Abrir o diálogo para selecionar uma pasta
        dialog = QFileDialog()
        selected_folder = dialog.getExistingDirectory()

        if selected_folder:
            
            names = get_names(selected_folder)
            global image_array
            image_array = []
            for name in names:
                pixmap = convert_dcm_png(selected_folder, name)
                image_array.append(pixmap)


            # O caminho da pasta selecionada agora está na variável selected_folder
            # Você pode fazer o que quiser com este caminho
            # Por exemplo, você pode carregar todas as imagens dessa pasta
            # ...
            print(f"Pasta selecionada: {selected_folder}")
        else:
            print("Seleção de pasta cancelada pelo usuário.")

        

        
    
    
    
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