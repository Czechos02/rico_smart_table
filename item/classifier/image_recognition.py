from keras.models import Sequential, load_model
from keras.layers import Conv2D, MaxPooling2D, Flatten, Dense, BatchNormalization, Dropout, ReLU, DepthwiseConv2D
from keras.optimizers import Adam

import os
import pickle
import pandas as pd
import numpy as np

from item.item import ItemType
from debug.debug import *


class Classifier:
    model = None
    trained = False
    output_types = None

    def __init__(self, num_classes=0, class_items=[]):
        if len(class_items) == num_classes and num_classes > 0:
            self.model = self.get_default_model(num_classes)
            self.output_types = class_items
            self.trained = False

    def trainModel(self, x_train, y_train, x_val, y_val, batch_size=16, epochs=100):
        if self.model is None:
            return -1
        self.model.fit(x_train, y_train, batch_size=batch_size, epochs=epochs, validation_data=(x_val, y_val))
        self.trained = True

    def predict(self, images):
        if self.trained:
            # For every image returns array of probabilities for that item
            predictions = self.model.predict(images, verbose=0)
            return predictions
        else:
            return []

    def predict_items_with_confidence(self, images, confidence_treshold, map_of_types):
        if self.trained:
            try:
                # For every image returns one most probable item, if probability value is greater than treshold
                predictions = self.model.predict(images, verbose=0)
                item_predictions = []
                for prediction in predictions:
                    max_val = np.argmax(prediction)
                    if prediction[max_val] > confidence_treshold:
                        item_predictions.append(ItemType(map_of_types[max_val]))
                    else:
                        item_predictions.append(ItemType.unknown)
                return item_predictions
            except:
                debug(DBGLevel.ERROR, "Item prediction failed")
                return [[ItemType.unknown]]
        else:
            return [[ItemType.unknown]]

    def export_model(self, filename):
        if self.trained:
            filename = os.path.splitext(filename)[0]
            # self.model.summary()
            self.model.save(filename + ".keras")
            with open(str(filename + ".names"), 'wb') as pickle_file:
                pickle.dump(self.output_types, pickle_file)
            debug(DBGLevel.WARN, "Model successfully exported")

    def import_model(self, filename):
        filename = os.path.splitext(filename)[0]
        self.model = load_model(filename + ".keras")
        # self.model.summary()
        with open(str(filename + ".names"), 'rb') as pickle_file:
            self.output_types = pickle.load(pickle_file)
        self.trained = True
        debug(DBGLevel.WARN, "Model successfully imported")

    def evaluate(self, images, labels):
        if self.trained:
            loss, accuracy = self.model.evaluate(images, labels)
            return accuracy

    def evaluationTable(self, images, labels):
        if self.trained:
            predictions = self.predict(images)

            # TODO change to panda
            # df = pd.DataFrame(predictions)

            pre_sum = np.zeros((labels.shape[1], labels.shape[1]))
            pre_nr = np.zeros((labels.shape[1], 1))

            for i, line in enumerate(predictions, start=0):
                np.add.at(pre_sum, np.argmax(labels[i]), line)
                np.add.at(pre_nr, np.argmax(labels[i]), 1)

            predictions_merged = pd.DataFrame(pre_sum / pre_nr)
            return predictions_merged

    def set_model(self, model, class_items, trained=False):
        self.model = model
        self.output_types = class_items
        self.trained = trained

    @staticmethod
    def get_default_model(num_classes):
        # Define the model architecture
        model = Sequential()

        model.add(Conv2D(16, (3, 3), input_shape=(16, 16, 1), padding="same", strides=1))
        model.add(BatchNormalization())
        model.add(ReLU())
        model.add(MaxPooling2D((2, 2), padding="same", strides=1))

        model.add(DepthwiseConv2D((3, 3), padding="same", strides=1))
        model.add(BatchNormalization())
        model.add(ReLU())

        model.add(Conv2D(32, (3, 3), padding="same", strides=1))
        model.add(BatchNormalization())
        model.add(ReLU())
        model.add(MaxPooling2D((2, 2)))

        model.add(Conv2D(64, (3, 3)))
        model.add(BatchNormalization())
        model.add(ReLU())

        model.add(Conv2D(128, (3, 3)))
        model.add(BatchNormalization())
        model.add(ReLU())

        model.add(Flatten())
        model.add(Dense(100, activation='relu'))
        model.add(Dropout(0.1))
        model.add(Dense(num_classes, activation='softmax'))

        # Compile the model
        model.compile(optimizer=Adam(learning_rate=0.01), loss='categorical_crossentropy', metrics=['accuracy'])
        # model.summary()
        return model
