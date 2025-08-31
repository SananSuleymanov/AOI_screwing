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


class nameWindow(QDialog):
    def __init__(self):
        super().__init__()

        self.selected_item = None

        self.setWindowTitle("Give name for receipe")
        
        self.layout_name = QHBoxLayout()
        self.label = QLabel("Name: ")
        self.name_edit = QLineEdit()
        self.layout_name.addWidget(self.label)
        self.layout_name.addWidget(self.name_edit)
        

        self.push_button = QPushButton("Save")
        

        self.layout = QVBoxLayout()
        #self.push_button.clicked.connect(self.save_parameters)

        self.layout.addLayout(self.layout_name)

        self.layout.addWidget(self.push_button)

        self.setLayout(self.layout)
        