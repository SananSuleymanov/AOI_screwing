from PySide6.QtCore import Qt, QThread, Signal, Slot, QSettings, QRectF
from PySide6.QtGui import QAction, QImage, QKeySequence, QPixmap, QPainter, QPen, QCursor
from PySide6.QtWidgets import (QApplication, QComboBox, QGroupBox,
                               QHBoxLayout, QLabel, QMainWindow, QPushButton,
                               QSizePolicy, QVBoxLayout, QWidget, QDialog, QLineEdit, QGraphicsView,
                               QGraphicsScene, QFileDialog, QCheckBox, QListWidget, QListWidgetItem, QRadioButton,
                               QGraphicsSceneMouseEvent, QMessageBox)


#warning message window

class warningbox(QMessageBox):
    def __init__(self, text):
        super().__init__()
        self.msg_text =text

        self.setText(self.msg_text)
        self.setIcon(QMessageBox.Warning)
        self.setWindowTitle("Warning")
        self.setStandardButtons(QMessageBox.Ok)