import numpy as np
import pandas as pd
import random
from copy import deepcopy

from item.item_utils import loadItems, selectDesiredItems, selectDesiredPlacement, rotate_item, flip_item
from item.item import ItemType, ItemPlacement
from item.classifier.image_utils import ImageParser, splitDataToTraining
from item.classifier.image_recognition import Classifier
from item.classifier.position_recognition import check_item_on_edge
from sensor.params import ImageMask
from languages.en import itemTranslationDict

path = "c_img_v2"
mask = ImageMask()
parser = ImageParser()

itemList = loadItems(path, mask.getMask())
itemList = selectDesiredItems(itemList, [ItemType.book,
                                         # ItemType.food_tray,
                                         ItemType.mug_full, ItemType.mug_empty,
                                         ItemType.plate_full, ItemType.plate_empty, ItemType.phone, ItemType.drug,
                                         ItemType.hand_any, ItemType.hand_hard, ItemType.hand_mid, ItemType.hand_light])
itemList = selectDesiredPlacement(itemList, [ItemPlacement.center, ItemPlacement.side, ItemPlacement.edge])

# Merge items of same type
for item in itemList:
    if item.type == ItemType.mug_empty or item.type == ItemType.mug_full:
        item.type = ItemType.mug_any
    if item.type == ItemType.plate_empty or item.type == ItemType.plate_full:
        item.type = ItemType.plate_any
    if item.type == ItemType.hand_light or item.type == ItemType.hand_mid or item.type == ItemType.hand_hard:
        item.type = ItemType.hand_any

# Remove items that would be classified by node as on edge
newList = []
for item in itemList:
    if not check_item_on_edge(item.getExtractedImage(), mask):
        newList.append(item)
itemList = newList

# Make every possible rotation of items
# TODO clean this shit up
newList = []
for item in itemList:
    item1 = deepcopy(item)
    item2 = deepcopy(item)
    item3 = deepcopy(item)
    item4 = deepcopy(item)
    item5 = deepcopy(item)
    item6 = deepcopy(item)
    item7 = deepcopy(item)
    item8 = deepcopy(item)

    item2 = rotate_item(item2, 90)
    item3 = rotate_item(item3, 180)
    item4 = rotate_item(item4, 270)

    item5 = flip_item(item5)
    item6 = flip_item(item6)
    item7 = flip_item(item7)
    item8 = flip_item(item8)

    item6 = rotate_item(item6, 90)
    item7 = rotate_item(item7, 180)
    item8 = rotate_item(item8, 270)

    newList.append(item1)
    newList.append(item2)
    newList.append(item3)
    newList.append(item4)
    newList.append(item5)
    newList.append(item6)
    newList.append(item7)
    newList.append(item8)
itemList = newList
random.shuffle(itemList)

# Make every class of items same size
labels = parser.parseLabelsToArray(itemList)
min_sum = int(min(labels.sum(axis=0)))
class_cnt = np.zeros(labels.shape[1], dtype=int)
newList = []
for i, item in enumerate(itemList, start=0):
    if class_cnt[np.argmax(labels[i])] < min_sum:
        class_cnt[np.argmax(labels[i])] += 1
        newList.append(item)
itemList = newList

# Split data to training
[trainingSet, validationSet, testSet] = splitDataToTraining(itemList, 7, 2, 1)

# Parsing images and labels so keras can use them
x_train = parser.parseImagesToArray(trainingSet)
y_train = parser.parseLabelsToArray(trainingSet)
x_val = parser.parseImagesToArray(validationSet)
y_val = parser.parseLabelsToArray(validationSet)
x_test = parser.parseImagesToArray(testSet)
y_test = parser.parseLabelsToArray(testSet)

classifier = Classifier()
##############################
# classifier.import_model("item/classifier/models/test_model.keras")
###############
classifier.set_model(Classifier.get_default_model(y_train.shape[1]),
                     parser.parseOrdinalNumbersToItemTypes(list(range(0, y_train.shape[1]))))
classifier.trainModel(x_train, y_train, x_val, y_val)
##############################

# Evaluate used model
table = classifier.evaluationTable(x_test, y_test)
column_names = parser.parseOrdinalNumbersToNames(list(range(0, y_train.shape[1])))
table.columns = column_names
table.index = column_names
print(table.to_string())
print("Accuracy: " + str(classifier.evaluate(x_test, y_test)))

# Check model for single item
im = np.array([x_test[5]])
elo = classifier.predict(im)
elo_ = classifier.predict_items_with_confidence(im, 0.7, classifier.output_types)
eluwina = pd.DataFrame(elo)
eluwina.columns = column_names
print(eluwina.to_string())
print(testSet[5].type)
print(itemTranslationDict[elo_[0]])

# Export model
# classifier.export_model("item/classifier/models/test_model.keras")
