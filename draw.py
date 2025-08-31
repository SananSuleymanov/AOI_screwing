import os
import sys
import time
import json
from typing import Optional, Sequence
import numpy as np

import cv2
from PySide6.QtCore import Qt, QThread, Signal, Slot, QSettings, QRectF
from PySide6.QtGui import QAction, QImage, QKeySequence, QPixmap, QPainter, QPen, QCursor
from PySide6.QtWidgets import (QApplication, QComboBox, QGroupBox,
                               QHBoxLayout, QLabel, QMainWindow, QPushButton,
                               QSizePolicy, QVBoxLayout, QWidget, QDialog, QLineEdit, QGraphicsView,
                               QGraphicsScene, QFileDialog, QCheckBox, QListWidget, QListWidgetItem, QRadioButton,
                               QGraphicsSceneMouseEvent)

from name import nameWindow
from warning import warningbox

class drawRectangle(QGraphicsView):
    def __init__(self, list):
        super().__init__()
        self.initUI()
        self.rectangles = []
        self.image = None
        self.selected_index = None
        self.const_index = None
        self.list = list
        self.setCursor(Qt.CrossCursor)

    def initUI(self):
        self.scene = QGraphicsScene()
        self.scene.setSceneRect(0, 0, 640, 480)
        self.setScene(self.scene)
        
        self.mousePressed = False
        self.startPoint = None
        self.endPoint = None


    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            print("yes")
            self.mousePressed = True
            self.startPoint = self.mapToScene(event.pos())
            print(self.startPoint)
            self.endPoint = self.startPoint
            if self.image:
                self.updateScene()

    def mouseMoveEvent(self, event):
        if self.mousePressed:
            self.endPoint = self.mapToScene(event.pos())
            print(self.endPoint)
            if self.image:
                self.updateScene()
    
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.mousePressed = False
            self.endPoint = self.mapToScene(event.pos())
            if self.image:
                self.rectangles.append(QRectF(self.startPoint, self.endPoint))
                self.updateScene()
                self.updateList()

    
    

    def updateScene(self):

        self.scene.clear()
        pixmap = QPixmap.fromImage(self.image)
        print(pixmap.size())

        self.scene.addPixmap(pixmap)

        painter = QPainter()
        painter.begin(pixmap)

        painter.setPen(QPen(Qt.red, 2, Qt.SolidLine))

        for rect in self.rectangles:
            painter.drawRect(rect)

        #resize operation
        
        if self.mousePressed:
            painter.drawRect(QRectF(self.startPoint, self.endPoint))

        if self.selected_index:
            print(self.selected_index)
            painter.setPen(QPen(Qt.blue, 2, Qt.SolidLine))
            painter.drawRect(self.rectangles[self.selected_index])

        painter.end()
        self.scene.addPixmap(pixmap)
        self.setScene(self.scene)

    def updateList(self):

        self.list.clear()
        for i, rect in enumerate(self.rectangles):
            item = QListWidgetItem(f"Point {i}")
            #: ({rect.topLeft().x()}, {rect.topLeft().y()},"
             #                      f"{rect.bottomRight().x()}, {rect.topRight().y()})
            self.list.addItem(item)

    def resize(self, rect, pos):
        
        top_left = QRectF(rect.topLeft().x(), rect.topLeft().y(), 
                        (rect.bottomRight().x()-rect.topLeft().x())/2, (rect.bottomRight().y()-rect.topLeft().y())/2)
            
            
        if top_left.contains(pos):
                    self.startPoint = self.mapToScene(pos)
                    self.endPoint = rect.bottomRight()

class drawWindow(QDialog):
    def __init__(self):
        super().__init__()

        self.selected_item = None
        self.status=None  #status for camera

        self.setWindowTitle("Create Receipe")
        self.setGeometry(100, 100, 950, 500)

        self.name_window = nameWindow()

        self.layout = QHBoxLayout()

        self.layout_two = QVBoxLayout()
        self.list = QListWidget()
        self.layout_two.addWidget(self.list)
        self.button_delete = QPushButton("Delete Item", self)
        self.button_delete.clicked.connect(self.delete)
        self.layout_two.addWidget(self.button_delete)

        self.button_save = QPushButton("Save Receipe", self)
        self.button_save.clicked.connect(self.save)
        self.layout_two.addWidget(self.button_save)
        
        self.list.clicked.connect(self.selected)


        self.drawlayout = drawRectangle(self.list)
        self.drawlayout.setFocusPolicy(Qt.StrongFocus)

        self.layout_one = QVBoxLayout()
        self.screw_check = QRadioButton("Classification")
        self.screw_check.setChecked(True)
        self.screw_check.toggled.connect(self.uncheck)
        self.layout_one.addWidget(self.screw_check)
        self.dispens_check = QRadioButton("Segmentation")
        self.dispens_check.toggled.connect(self.uncheck)
        self.layout_one.addWidget(self.dispens_check)

        self.layout_one.addWidget(self.drawlayout)
        self.button_image = QPushButton("Choose Image", self)
        self.button_image.clicked.connect(self.open_image)
        self.layout_one.addWidget(self.button_image)

        self.button_video = QPushButton("Take Picture", self)
        self.button_video.clicked.connect(self.open_camera)
        self.layout_one.addWidget(self.button_video)
        

        self.layout.addLayout(self.layout_one, 70)
        self.layout.addLayout(self.layout_two, 30)

        self.setLayout(self.layout)

        self.x1 = None
        self.y1 = None
        self.w1 = None
        self.h1 = None

        #save receipe when save button clicked
        
        self.name_window.push_button.clicked.connect(self.save_receipe)


    @Slot()
    def open_image(self):
        self.filename, _ = QFileDialog.getOpenFileName(self, "Open Image", "", "Image Files (*.png *.jpg *.bmp)")
        print(self.filename)
        self.status =False
        if self.filename:
            image_color = cv2.imread(self.filename, cv2.IMREAD_COLOR)
            img_resize = cv2.resize(image_color, (640, 480), cv2.INTER_LINEAR)
            h, w, ch = img_resize.shape
            img_resize, self.x1,self.y1, self.w1, self.h1 = background(img_resize).find()
            self.image_init = QImage(img_resize, w, h, ch*w, QImage.Format_RGB888)
            #self.image = self.image_init.scaled(500, 500, Qt.KeepAspectRatio)
            pixmap = QPixmap.fromImage(self.image_init)
            self.drawlayout.image = self.image_init
            self.drawlayout.rectangles = []
            self.drawlayout.scene.clear()
            self.drawlayout.scene.addPixmap(pixmap)

    @Slot()
    def open_camera(self):
        self.cap = cv2.VideoCapture(0)

        self.drawlayout.rectangles = []
        self.drawlayout.scene.clear()
        self.status =True

        if not self.cap.isOpened():
            print("Error: Could not open camera capture")

        
        ret, frame = self.cap.read()
            
        
        
        color_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img_resize = cv2.resize(color_frame, (640, 480), cv2.INTER_LINEAR)
        h, w, ch = img_resize.shape
        img_resize, self.x1,self.y1, self.w1, self.h1 = background(img_resize).find()
        self.image_init = QImage(img_resize, w, h, ch*w, QImage.Format_RGB888)
         #self.image = self.image_init.scaled(500, 500, Qt.KeepAspectRatio)
        pixmap = QPixmap.fromImage(self.image_init)
        self.drawlayout.image = self.image_init
            
        self.drawlayout.scene.addPixmap(pixmap)
        self.cap.release()
        


    @Slot()
    def selected(self, qmodelindex):
        self.selected_item = self.list.currentItem()
        self.drawlayout.selected_index = self.list.row(self.selected_item)
        self.drawlayout.updateScene()
        
        

    @Slot()
    def delete(self):
        if self.list.currentItem():
            item = self.list.row(self.selected_item)
            print(self.drawlayout.rectangles)
            self.drawlayout.rectangles.remove(self.drawlayout.rectangles[item])
            self.drawlayout.selected_index = None
            self.drawlayout.updateScene()
            self.drawlayout.updateList()
            print("delete: ", self.selected_item)

    @Slot()
    def save(self):
        if self.drawlayout.rectangles:
            self.name_window.exec_()
        else:
            self.message_w = warningbox("Receipe can't be empty")
            self.message_w.exec_()

    @Slot()
    def save_receipe(self):
        
        name_receipe = self.name_window.name_edit.text()
        print(name_receipe)
        if name_receipe:
            items = [self.list.item(x).text() for x in range(self.list.count())]
            save_rec_coordinates = {}
            for item, rect in zip(items, self.drawlayout.rectangles):
                save_rec_coordinates[item] = [rect.topLeft().x(), rect.topLeft().y(), rect.bottomRight().x(),
                                rect.bottomRight().y()]
            
            receipe={}
            if self.screw_check.isChecked():
                receipe["name"] = "Module_2"
                receipe["area_object"] = [self.x1, self.y1, self.w1, self.h1]
                receipe["coordinates"] = save_rec_coordinates
                with open("recipes/classification/"+name_receipe+".json", "w") as file:
                    json.dump(receipe, file)
                self.name_window.close()
                self.close()
            elif self.dispens_check.isChecked():
                receipe["name"] = "Module_1"
                receipe["coordinates"] = save_rec_coordinates
                receipe["area_object"] = [self.x1, self.y1, self.w1, self.h1]
                with open("recipes/segmentation/"+name_receipe+".json", "w") as file:
                    json.dump(receipe, file)
                self.status =False
                self.name_window.close()
                self.close()

        else:
            self.message_w = warningbox("Give name for receipe")
            self.message_w.exec_()
        print(receipe)
            
    @Slot()
    def uncheck(self, state):
        print("check")
        

    

    
class background():
    def __init__(self, image):
        self.image = image
        self.mask = np.zeros(image.shape[:2], dtype="uint8")
        self.fgModel = np.zeros((1, 65), dtype=float)
        self.bgModel = np.zeros((1, 65), dtype=float)
        self.rectangel = (50, 50, 450,450 )
    
    def find(self):
        (mask, fgModel, bgModel) = cv2.grabCut(self.image, self.mask,self.rectangel, 
                                               self.fgModel, self.bgModel, iterCount=10, 
                                               mode=cv2.GC_INIT_WITH_RECT)
        mask2 = np.where((mask==2)| (mask==0), 0, 1).astype('uint8')

        contours, _ =cv2.findContours(mask2, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE )

        object_counter = max(contours, key=cv2.contourArea)
        x,y, w, h = cv2.boundingRect(object_counter)
        cv2.rectangle(self.image, (x, y), (x+w, y+h), (0, 255, 0), 2)
        
        return self.image, x, y, w, h
        
