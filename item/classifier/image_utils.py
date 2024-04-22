import numpy as np
import pandas as pd
import keras
import cv2
import matplotlib.pyplot as plt

from item.item import Item, ItemType


class LabelsMap:
    instance = None
    map = None
    reverse_map = None

    # Singleton
    def __new__(cls, *args, **kwargs):
        if not isinstance(cls.instance, cls):
            cls.instance = object.__new__(cls)
        return cls.instance

    def __init__(self, labelList):
        self.setMapFromLabels(labelList)

    def setMapFromLabels(self, labellist):
        df = pd.DataFrame([labellist])
        v = df.stack().unique()
        v.sort()
        f = pd.factorize(v)
        self.map = pd.Series(f[0], f[1])
        self.reverse_map = pd.Series(f[1], f[0])

    def mapLabelsToOrdinalNumbers(self, labellist):
        df = pd.DataFrame([labellist])
        ordinalNumbers = df.stack().map(self.map).unstack()
        return ordinalNumbers

    def mapOrdinalNumbersToLabels(self, ordinalNumbers):
        df = pd.DataFrame([ordinalNumbers])
        labels = df.stack().map(self.reverse_map).unstack()
        return labels

    def mapOrdinalNumbersToLabelNames(self, ordinalNumbers):
        from languages import en as translation

        labels = self.mapOrdinalNumbersToLabels(ordinalNumbers)
        labels = labels.values
        labelNames = []
        for label in labels:
            for jebanyPython in label:
                elo = translation.itemTranslationDict[ItemType(jebanyPython)]
                labelNames.append(elo)
        return labelNames


class ImageParser:
    map = None

    def parseImagesToArray(self, itemlist):
        imageList = []
        for item in itemlist:
            # imageList.append(np.array(item.image))  # - np.array(item.image_calibration))
            imageList.append(np.array(item.image_extracted))
        imageList = np.array(imageList)
        return imageList

    def parseLabelsToArray(self, itemlist):
        labelList = []
        for item in itemlist:
            labelList.append(item.type.value)

        self.map = LabelsMap(labelList)
        labelList = self.map.mapLabelsToOrdinalNumbers(labelList)
        labelList = np.array(keras.utils.to_categorical(labelList))
        labelList = np.hstack(labelList)
        labelList = np.array(labelList)
        return labelList

    def parseWeightsToArray(self, itemlist):
        weightList = []
        for item in itemlist:
            weightList.append(item.weight)

        return np.array(weightList)

    def parseOrdinalNumbersToNames(self, list):
        return self.map.mapOrdinalNumbersToLabelNames(list)

    def parseOrdinalNumbersToItemTypes(self, list):
        df = self.map.mapOrdinalNumbersToLabels(list)
        return df.values.tolist()[0]


def splitDataToTraining(data, training_size, valuation_size, test_size=0.0):
    # Normalize inputs
    # all_weight = training_size + valuation_size + test_size
    # training_size /= all_weight
    # valuation_size /= all_weight
    # test_size /= all_weight

    train_data = []
    val_data = []
    test_data = []
    # This part is bad but I dont care
    modulo_idx = 0
    for item in data:
        modulo_idx = modulo_idx % int(training_size + valuation_size + test_size)
        if modulo_idx < training_size:
            train_data.append(item)
        elif modulo_idx < training_size + valuation_size:
            val_data.append(item)
        else:
            test_data.append(item)
        modulo_idx += 1
    # End of bad part

    if test_size > 0.0:
        return [train_data, val_data, test_data]
    return [train_data, val_data]


def stretch_image(image, stretch_x, stretch_y):
    image = np.uint8(image)
    stretched_image = cv2.resize(image, None, fx=stretch_x, fy=stretch_y, interpolation=cv2.INTER_LINEAR)
    stretched_image = np.uint8(stretched_image)
    return stretched_image


def plot_learning_curve(history):
    loss = history.history['loss']
    val_loss = history.history['val_loss']
    epochs = range(1, len(loss) + 1)

    plt.figure(figsize=(12, 6))
    plt.plot(epochs, loss, 'r-', label='Training loss')
    plt.plot(epochs, val_loss, 'b', label='Validation loss')
    plt.title('Training and Validation Loss')
    plt.xlabel('Epochs')
    plt.ylabel('Loss')
    plt.legend()
    plt.show()
