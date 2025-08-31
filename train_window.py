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

#Train window consists of the layout for each steps
#Step 1: Choose task; classification, segmentation
#Step 2: Select Images 
#Step 3: Prepare dataset; Labeling selected images
#Step 4: Start training; progress bar
#Step 5: Finish - model saved

class trainwindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setGeometry(100, 100, 950, 500)
        self.layout = QHBoxLayout()
        self.layout_steps = QVBoxLayout()

        self.step1 = QLabel('Step 1: Choose task')
        self.step2 = QLabel('Step 2: Select Images')
        self.step3 = QLabel('Step 3: Prepare dataset')
        self.step4 = QLabel('Step 4: Start Training')
        self.step5 = QLabel('Step 5: Finish')
        self.layout_steps.addWidget(self.step1)
        self.layout_steps.addWidget(self.step2)
        self.layout_steps.addWidget(self.step3)
        self.layout_steps.addWidget(self.step4)
        self.layout_steps.addWidget(self.step5)

        self.layout_screen = QVBoxLayout()

        self.layout.addLayout(self.layout_steps, 20)
        self.layout.addLayout(self.layout_screen, 80)

        self.setLayout(self.layout)

"""
class UIselecttask(QWidget):
    def setUI(self):
        self.layout = QVBoxLayout()
        self.label1 = QLabel('Choose Task')

        
"""
        