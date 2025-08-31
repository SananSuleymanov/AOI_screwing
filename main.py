import os
import sys
import time
import json
from typing import Optional
import tensorflow as tf
import numpy as np

import cv2
from PySide6.QtCore import Qt, QThread, Signal, Slot, QSettings, QFile, QTextStream
from PySide6.QtGui import QAction, QImage, QKeySequence, QPixmap, QIcon
from PySide6.QtWidgets import (QApplication, QComboBox, QGroupBox,
                               QHBoxLayout, QLabel, QMainWindow, QPushButton,
                               QSizePolicy, QVBoxLayout, QWidget, QDialog, QLineEdit)
from draw import drawWindow
from predict import predict
from train_window import trainwindow

settings = QSettings("YourOrganizationName", "YourApplicationName")

#color for text and boxes
color_code = [ (255, 0, 0), (0, 255,0)]
class Thread(QThread):
    updateframe = Signal(QImage)

    def __init__(self, parent = None):
        QThread.__init__(self, parent=parent)
        self.status =True
        self.receipe = None
        self.operation = "Screwing"
        self.img_height = 25
        self.img_width = 25
        self.color_frame = None
    
    def coordinate(self):
        if self.operation == "Classification":
            path = os.path.join(".\\recipes\\classification", self.receipe)
            print(self.receipe)
            json_file = open(path)
            data = json.load(json_file)

        elif self.operation == "Segmentation":
            path = os.path.join(".\\recipes\\segmentation", self.receipe)
            json_file = open(path)
            data = json.load(json_file)
        
        return data
            


    def run(self):
        self.cap = cv2.VideoCapture("try.mp4")

        if not self.cap.isOpened():
            print("Error: Could not open camera capture")

        while self.status:
            ret, frame = self.cap.read()
            
            if not ret:
                print("Error: Could not open camera capture")
                break
        
            color_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            color_frame = cv2.resize(color_frame, (640, 480), cv2.INTER_LINEAR)

            h, w, ch = color_frame.shape
            data = self.coordinate()["coordinates"]
            img_ = [] #array of cropped images for running prediction
        
            for key, value in data.items():
                
                #cropes images and convert to array
                crop = color_frame[int(value[1]): int(value[3]), 
                                   int(value[0]): int(value[2])]
                
                crop = tf.image.resize(crop, (self.img_height, self.img_width))
                
                img_.append(crop)
            img_array1 = np.array(img_)
            
            predictions = predict().predict_screw(img_array1) #runs predictions

            object_area = self.coordinate()["area_object"]
            for i, (key, value) in enumerate(data.items()):
                
                cv2.rectangle(color_frame, (object_area[0], object_area[1]), 
                              (object_area[0]+object_area[2], object_area[1]+object_area[3]), 
                              (0, 255, 0), 2)
                
                cv2.rectangle(color_frame, (int(value[0]), int(value[1])), (int(value[2]),int(value[3])),
                                                                  color_code[predictions[i]], 2)
            #image with text
            color_frame = self.text(color_frame, predictions)
            img = QImage(color_frame, w, h, ch*w, QImage.Format_RGB888)
            #scaled_img = img.scaled(500, 500, Qt.KeepAspectRatio)

            self.updateframe.emit(img)
        
        sys.exit(-1)
    
    def text(self, image, list):
        # font 
        font = cv2.FONT_HERSHEY_SIMPLEX 
        # org 
        org = (50, 50) 
        # fontScale 
        fontScale = 1
        thickness =2

        status = True

        for i in list:
            if i !=1:
                status = False
                break
        if status == True:
            cv2.putText(image, 'Pass', org, font, fontScale, color_code[1], thickness, cv2.LINE_AA)
        elif status == False:
            cv2.putText(image, 'Fail', org, font, fontScale, color_code[0], thickness, cv2.LINE_AA)

        return image

 


class ApiWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("HTTP Request")
        self.setGeometry(100, 100, 400, 200)

        self.layout_url = QHBoxLayout()
        self.label = QLabel("URL: ")
        self.url_edit = QLineEdit()
        self.layout_url.addWidget(self.label)
        self.layout_url.addWidget(self.url_edit)
        

        self.layout_header = QHBoxLayout()
        self.label_h = QLabel("Header: ")
        self.h_edit = QLineEdit()
        self.layout_header.addWidget(self.label_h)
        self.layout_header.addWidget(self.h_edit)


        self.push_button = QPushButton("Save")
        

        self.layout = QVBoxLayout()
        self.push_button.clicked.connect(self.save_parameters)

        self.layout.addLayout(self.layout_url)
        self.layout.addLayout(self.layout_header)
        self.layout.addWidget(self.push_button)

        self.setLayout(self.layout)
        self.load_parameters()

    @Slot()
    def load_parameters(self):
        url = settings.value("url", "")
        header = settings.value("header", "")
        self.url_edit.setText(url)
        self.h_edit.setText(header)


    @Slot()
    def save_parameters(self):
        settings.setValue("url", self.url_edit.text())
        settings.setValue("header", self.h_edit.text())

class Window(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon('logo/logo.png'))
        self.setWindowTitle("CubedAI - AOI")
        self.setGeometry(0, 0, 300, 300)

        self.menu = self.menuBar()
        self.menu_file = self.menu.addMenu("File")
        exit = QAction("Exit", self, triggered=QApplication.quit)
        self.menu_file.addAction(exit)

        self.menu_about = self.menu.addMenu("&About")
        about = QAction("About CubedAI", self, shortcut = QKeySequence(QKeySequence.HelpContents),
                        triggered = QApplication.aboutQt)
        self.menu_about.addAction(about)
        
        self.menu_api = self.menu.addMenu("API")
        api = QAction("HTTP Request", self)
        api.triggered.connect(self.open_api)
        self.menu_api.addAction(api)

        self.menu_draw = self.menu.addMenu("Create Receipe")
        draw = QAction("Create Receipe", self)
        draw.triggered.connect(self.open_draw)
        self.menu_draw.addAction(draw)

        self.menu_train = self.menu.addMenu("Train Model")
        train = QAction("Train", self)
        train.triggered.connect(self.open_train)
        self.menu_train.addAction(train)


        self.label = QLabel(self)
        #self.label.setFixedSize(1280, 960)

        self.th = Thread(self)
        self.th.finished.connect(self.close)
        self.th.updateframe.connect(self.setImage)

        self.group_model = QGroupBox("Model Selection")
        self.group_model.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        model_layout = QHBoxLayout()

        self.selection_box = QVBoxLayout()

        
        self.combo_layout2 = QHBoxLayout()

        self.combo_box2 = QComboBox()
        self.combo_box2.addItem('Classification')
        self.combo_box2.addItem('Segmentation')

        self.combo_layout2.addWidget(QLabel('Process: '), 10)
        self.combo_layout2.addWidget(self.combo_box2, 90)


        self.combo_layout1 = QHBoxLayout()
        self.combo_box= QComboBox()
        if self.combo_box2.currentText() =='Classification':
            for receibe_json in os.listdir('./recipes/classification'):
                if receibe_json.endswith(".json"):
                    self.combo_box.addItem(receibe_json)
        elif self.combo_box2.currentText() =='Segmentation':
            for receibe_json in os.listdir('./recipes/segmentation'):
                if receibe_json.endswith(".json"):
                    self.combo_box.addItem(receibe_json)


        self.combo_layout1.addWidget(QLabel('Recipes: '), 10)
        self.combo_layout1.addWidget(self.combo_box, 90)

        self.selection_box.addLayout(self.combo_layout2)
        self.selection_box.addLayout(self.combo_layout1)


        model_layout.addLayout(self.selection_box, 90)
        model_layout.setAlignment(Qt.AlignTop)
        self.group_model.setLayout(model_layout)
        
        buttons_layout = QHBoxLayout()
        self.button1 = QPushButton("Start")
        self.button2 = QPushButton("Stop/Close")
        #self.button1.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        #self.button1.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.button1.setFixedWidth(150)
        self.button1.setFixedHeight(70)

        self.button2.setFixedWidth(150)
        self.button2.setFixedHeight(70)
        self.button2.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)



        buttons_layout.addWidget(self.button1)
        buttons_layout.addWidget(self.button2)

        right_layout = QHBoxLayout()
        right_layout.addWidget(self.group_model, 1)
        right_layout.setAlignment(Qt.AlignTop)
        right_layout.addLayout(buttons_layout, 1)
        

        layout = QVBoxLayout()
        layout.addLayout(right_layout)
        layout.setAlignment(Qt.AlignTop)
        layout.addWidget(self.label, 3)
        
        
        widget = QWidget(self)
        widget.setLayout(layout)
        self.setCentralWidget(widget)

        self.button1.clicked.connect(self.start)
        self.button2.clicked.connect(self.kill)
        self.button2.setEnabled(False)
        self.combo_box2.currentTextChanged.connect(self.change)
        self.combo_box.currentTextChanged.connect(self.change_1)

        
        #style set

        stylesheet_file = QFile("styles/main.css")
        if stylesheet_file.open(QFile.ReadOnly | QFile.Text):
            stream = QTextStream(stylesheet_file)
            stylesheet = stream.readAll()
            self.setStyleSheet(stylesheet)
    
    @Slot()
    def open_draw(self, checked):
        w1 = drawWindow()
        w1.exec_()

    @Slot()
    def open_api(self, checked):
        w1 = ApiWindow()
        w1.exec_()
        
    @Slot()
    def change_1(self, text):
        self.button1.setEnabled(True)
        self.button2.setEnabled(False)

    @Slot()
    def change(self, text):
        self.combo_box.clear()
        
        if text=='Classification':
            for receibe_json in os.listdir('./recipes/classification'):
                if receibe_json.endswith(".json"):
                    self.combo_box.addItem(receibe_json)
        elif text =='Segmentation':
            for receibe_json in os.listdir('./recipes/segmentation'):
                if receibe_json.endswith(".json"):
                    self.combo_box.addItem(receibe_json)

    @Slot()
    def kill(self):
        self.button1.setEnabled(True)
        self.button2.setEnabled(False)

        self.th.cap.release()
        cv2.destroyAllWindows()
        self.status= False
        self.th.terminate()
        time.sleep(1)
            

    @Slot()
    def start(self):
        self.button1.setEnabled(False)
        self.button2.setEnabled(True)
        receipe = self.combo_box.currentText()
        operation = self.combo_box2.currentText()
        
        self.th.receipe = receipe
        self.th.operation = operation
        self.th.start()

    

    @Slot()
    def setImage(self, image):
        label_size = self.label.size()

        scaled_image = QPixmap.fromImage(image).scaled(label_size, Qt.IgnoreAspectRatio)
        self.label.setPixmap(scaled_image)

    @Slot()
    def open_train(self):
        w1 = trainwindow()
        w1.exec_()


if __name__ == "__main__":
    app = QApplication([])
    widget = Window()
   
    widget.show()
    sys.exit(app.exec())

