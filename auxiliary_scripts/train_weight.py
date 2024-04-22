import numpy as np
import random
import matplotlib.pyplot as plt

from keras.models import load_model

from item.item_utils import loadItems, selectDesiredItems, selectDesiredPlacement
from item.item import ItemType, ItemPlacement
from item.classifier.image_utils import ImageParser, splitDataToTraining
from item.classifier.weight_estimation import get_default_weight_estimation_model, mean_absolute_percentage_square_error
from sensor.params import ImageMask
from sensor.data_parsing import flatten

# Definitions
path = "c_img_v2"
model_path = "../item/classifier/models/weight_model.keras"
mask = ImageMask()
parser = ImageParser()
shape = (16, 16, 1)
model = get_default_weight_estimation_model()

# Load items
itemList = loadItems(path, mask.getMask())
itemList = selectDesiredItems(itemList, [ItemType.book, ItemType.food_tray, ItemType.mug_full, ItemType.mug_empty,
                                         ItemType.plate_full, ItemType.plate_empty, ItemType.phone, ItemType.drug,
                                         ItemType.hand_any, ItemType.hand_hard, ItemType.hand_mid, ItemType.hand_light])
itemList = selectDesiredPlacement(itemList, [ItemPlacement.center, ItemPlacement.side])
random.shuffle(itemList)

# Remove items that would be classified by node as on edge
# newList = []
# for item in itemList:
#     if not check_item_on_edge(item.getExtractedImage(), mask):
#         newList.append(item)
# itemList = newList

# Split data to training
[trainingSet, validationSet, testSet] = splitDataToTraining(itemList, 7, 2, 1)

# Parsing images and labels so keras can use them
x_train = parser.parseImagesToArray(trainingSet)
y_train = parser.parseWeightsToArray(trainingSet)
x_val = parser.parseImagesToArray(validationSet)
y_val = parser.parseWeightsToArray(validationSet)
x_test = parser.parseImagesToArray(testSet)
y_test = parser.parseWeightsToArray(testSet)

##############################
model = load_model(model_path,
                   custom_objects={'mean_absolute_percentage_square_error': mean_absolute_percentage_square_error})
###############
# history = model.fit(x_train, y_train, batch_size=16, epochs=50, validation_data=(x_val, y_val))
##############################

# Evaluate used model
y_pred = np.array(flatten(model.predict(x_test, verbose=0)))
y_diff = y_pred - y_test
y_diff_a = np.abs(y_diff)
y_diff_rel = np.round((y_diff / y_test) * 100, 2)
y_diff_arel = np.abs(y_diff_rel)
y_var = model.evaluate(x_test, y_test, verbose=0)
print("Min: " + str(min(y_diff_rel)) + "%\tMax: " + str(max(y_diff_rel)) + "%")
print("Avg err: " + str(np.average(y_diff_a)))
print("Avg % err: " + str(np.average(y_diff_arel)))
print("Var: " + str(y_var))
print("Stand diff: " + str(np.sqrt(y_var)))

# Plot the histogram from test
plt.figure(figsize=(12, 6))
plt.hist(y_diff_arel, list(range(0, 101, 4)), rwidth=0.8)
plt.xlabel('Percentage deviation from the correct value')
plt.ylabel('Number of samples')
plt.title('Histogram of network learning results for object weight recognition')
plt.show()

# Plot learning curve
# plot_learning_curve(history)

# Check model for single item
print("Predicted: " + str(model.predict(np.array([x_test[5]]), verbose=0)))
print("Real: " + str(testSet[5].weight))

# Export model
# model.save(model_path)
