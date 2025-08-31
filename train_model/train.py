import sys
import tensorflow as tf
import matplotlib.pyplot as plt

import numpy as np
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.models import Sequential


sys.path.insert(0, '..')
from name_generator import generate_random_filename


data_dir = "/train/crop"

AUTOTUNE = tf.data.AUTOTUNE

class train():
    def __init__(self):
      self.task = 'classification' #default
      self.epochs=10
      self.batch_size = 16
      self.img_height = 25
      self.img_width = 25
        
      self.train_ds = tf.keras.utils.image_dataset_from_directory(
      data_dir,
      validation_split=0.2,
      subset="training",
      seed=123,
      image_size=(self.img_height, self.img_width),
      batch_size=self.batch_size)

      self.val_ds = tf.keras.utils.image_dataset_from_directory(
      data_dir,
      validation_split=0.2,
      subset="validation",
      seed=123,
      image_size=(self.img_height, self.img_width),
      batch_size=self.batch_size)

      self.class_names = self.train_ds.class_names


    def preprocess(self):
      train_ds = self.train_ds.cache().shuffle(1000).prefetch(buffer_size=AUTOTUNE)
      val_ds = self.val_ds.cache().prefetch(buffer_size=AUTOTUNE)

      normalization_layer = layers.Rescaling(1./255)

      normalized_ds = train_ds.map(lambda x, y: (normalization_layer(x), y))
      image_batch, labels_batch = next(iter(normalized_ds))
      return normalized_ds, val_ds

    def model_run(self):
      train_dt, val_dt = self.preprocess()

      num_classes = len(self.class_names)
      model = Sequential([
        layers.Rescaling(1./255, input_shape=(self.img_height, self.img_width, 3)),
        layers.Conv2D(16, 3, padding='same', activation='relu'),
        layers.MaxPooling2D(),
        layers.Conv2D(32, 3, padding='same', activation='relu'),
        layers.MaxPooling2D(),
        layers.Conv2D(64, 3, padding='same', activation='relu'),
        layers.MaxPooling2D(),
        layers.Flatten(),
        layers.Dense(128, activation='relu'),
        layers.Dense(num_classes)
      ])

      model.compile(optimizer='adam',
                    loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
                    metrics=['accuracy'])


      history = model.fit(
        train_dt,
        validation_data= val_dt,
        epochs=self.epochs
      )

      model_name = 'models/'+self.task+'/'+generate_random_filename(input='model')+'.keras'
      model.save(model_name)

