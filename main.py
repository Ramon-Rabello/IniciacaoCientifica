from PyQt6.QtWidgets import *
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import pydicom
import sys

def main():
    def func1():
        label.setText("clicou no botão")
        label.adjustSize()
    def func2():
        label.setText("volta pae")
        label.adjustSize()
    def func3():
        valor_lido = le.text()
        label.setText(valor_lido)
        label.adjustSize()
    def func4():
        valor_lido = le.text()
        filename = (f"./normal-dcm-anonymized/{valor_lido}.dcm")
        ds = pydicom.dcmread(filename)
        rect = Rectangle((250, 1250), 200, 100, fill=False)
        plt.gca().add_patch(rect)
        plt.imshow(ds.pixel_array, cmap=plt.cm.bone)
        # plt.colorbar()
        plt.show()

    app = QApplication(sys.argv)
    window = QWidget()
    window.resize(800,600)
    window.setWindowTitle('coisa linda')
    

    btn = QPushButton("botão1", window)
    btn.setGeometry(100,100,150,80)
    btn.setStyleSheet('color: green; background-color:blue')
    btn.clicked.connect(func1)

    btn2 = QPushButton("botão2", window)
    btn2.setGeometry(100,300,150,80)
    btn2.setStyleSheet('color: red; background-color:white')
    btn2.clicked.connect(func2)

    btn3 = QPushButton("botão3", window)
    btn3.setGeometry(100,500,150,80)
    btn3.setStyleSheet('color: red; background-color:gray')
    btn3.clicked.connect(func4)

        
    label = QLabel("show", window)
    label.move(400,200)
    label.setStyleSheet('font-size:30px')

    le=QLineEdit("",window)
    le.setGeometry(500,300,150,40)

    window.show()
    app.exec()
    
if __name__ == '__main__':
    main()