import tensorflow as tf
import numpy as np
from tensorflow import keras
import cv2

class predict():
    def __init__(self):
        self.model_0 = tf.keras.models.load_model('models/my_model.h5')
        self.class_names = ['non-screw', 'screw']
    
    def predict_screw(self, img_array):
        self.predictions = self.model_0.predict(img_array)
        print(self.predictions)
        score_all = []
        for i in self.predictions:
            score = tf.nn.softmax(i)
            score_bin = np.argmax(score)
            score_all.append(score_bin)
        print("score",score_all)
        return score_all
        #self.class_names[np.argmax(score)], 100 * np.max(score)
        """print(
        "This image most likely belongs to {} with a {:.2f} percent confidence."
        .format(self.class_names[np.argmax(score)], 100 * np.max(score))
    )"""
