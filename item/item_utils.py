import os
import numpy as np

from item.item import Item


def loadItems(path, mask=None):
    item_id = 1
    item_list = []

    files = os.listdir(path)
    for file in files:
        # Omit calibration images
        if file.startswith("c_"):
            continue

        new_item = Item(mask)
        new_item.getLabelsFromFilename(path, file, item_id)
        item_list.append(new_item)
        item_id += 1
    return item_list


def selectDesiredItems(all_items, item_filter):
    selected_items = []

    for item in all_items:
        if item.type in item_filter:
            selected_items.append(item)

    return selected_items


def selectDesiredPlacement(all_items, placement_filter):
    selected_items = []

    for item in all_items:
        if item.placement in placement_filter:
            selected_items.append(item)

    return selected_items


def selectCorruptedItems(all_items):
    corrupted_items = []

    for item in all_items:
        if item.potentially_corrupted is True:
            corrupted_items.append(item)

    return corrupted_items


def ommitCorruptedItems(all_items):
    good_items = []

    for item in all_items:
        if item.potentially_corrupted is False:
            good_items.append(item)

    return good_items


def rotate_item(item, angle=0):
    if angle == 90:
        k = 1
    elif angle == 180:
        k = 2
    elif angle == 270:
        k = 3
    else:
        return item

    item.image = np.rot90(item.image, k=k)
    item.image_calibration = np.rot90(item.image_calibration, k=k)
    item.image_mask = np.rot90(item.image_mask, k=k)
    item.image_extracted = np.rot90(item.image_extracted, k=k)
    # TODO extracted raw
    return item


def flip_item(item, plane="h"):
    if plane == "h":
        item.image = np.fliplr(item.image)
        item.image_calibration = np.fliplr(item.image_calibration)
        item.image_mask = np.fliplr(item.image_mask)
        item.image_extracted = np.fliplr(item.image_extracted)
    if plane == "v":
        item.image = np.flipud(item.image)
        item.image_calibration = np.flipud(item.image_calibration)
        item.image_mask = np.flipud(item.image_mask)
        item.image_extracted = np.flipud(item.image_extracted)
    # TODO extracted raw
    return item
