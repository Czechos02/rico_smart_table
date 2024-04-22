import numpy as np
import cv2

from item.item import ItemPlacement
from sensor.params import ImageMask
from debug.debug import debug, DBGLevel
from item.classifier.image_utils import stretch_image


def get_image_centroid(image, output_type):
    moments = cv2.moments(image)
    centroid_x = (moments["m10"] / moments["m00"])
    centroid_y = (moments["m01"] / moments["m00"])

    if output_type is float:
        centroid_x = round(centroid_x, 2)
        centroid_y = round(centroid_y, 2)
    elif output_type is int:
        centroid_x = int(round(centroid_x))
        centroid_y = int(round(centroid_y))
    else:
        centroid_x = int(round(centroid_x))
        centroid_y = int(round(centroid_y))

    return [centroid_x, centroid_y]


def find_histogram_peak(histogram, can_ret_none=True):
    idx_max_val = np.argmax(histogram)
    idx_all_max_vals = np.where(histogram == histogram[idx_max_val])

    # Multipeak
    if len(idx_all_max_vals[0]) > 1:
        for i in range(len(idx_all_max_vals[0]) - 1):
            if idx_all_max_vals[0][i + 1] - idx_all_max_vals[0][i] != 1:
                if can_ret_none:
                    return -1
                else:
                    return np.max(idx_all_max_vals)

        # Neighbour peaks
        idx_avg = np.average(idx_all_max_vals)
        return idx_avg

    return idx_max_val


def get_distance_to_mask(image_mask, point):
    e_image_mask = np.pad(image_mask, [(1, 1), (1, 1)], mode='constant', constant_values=0)
    point[0] += 1
    point[1] += 1

    distances = np.round(
        np.sqrt(
            (np.where(e_image_mask == 0)[1] - point[0]) ** 2 + (
                    np.where(e_image_mask == 0)[0] - point[1]) ** 2), 2)
    return np.min(distances)


def get_histogram_of_weight_from_point(image, point):
    # Calculate the distances from each white pixel to the centroid on the original image
    distances = np.uint8(np.round(np.sqrt(
        (np.where(image > 0)[1] - point[0]) ** 2 + (
                np.where(image > 0)[0] - point[1]) ** 2)))

    # Collect intensity values of the original image at corresponding distances
    intensity_values = np.uint32(image[image > 0])

    nrs, vals = np.unique(distances, return_counts=True)

    # If there is lack of some values add them to make full histogram (especially near 0)
    if len(nrs) is not max(nrs) + 1:
        new_nrs = []
        new_vals = []
        for i in range(max(nrs) + 1):
            new_nrs.append(i)
            if i in nrs:
                nr_id = np.where(nrs == i)[0][0]
                new_vals.append(vals[nr_id])
            else:
                new_vals.append(1)
        nrs = np.array(new_nrs)
        vals = np.array(new_vals)

    # Create a histogram of intensity values at corresponding distances
    hist_values, bins = np.histogram(distances, bins=len(nrs), weights=intensity_values, range=(0, nrs.max()))
    hist_values_weight = np.uint16(np.round(hist_values / vals))

    # Plot the cumulative histogram
    # plt.plot(bins[:-1], hist_values_weight)
    # plt.xlabel('Distance from Center')
    # plt.ylabel('Cumulative Intensity')
    # plt.title('Cumulative Histogram of Intensity vs. Distance from Center')
    # plt.show()

    return hist_values_weight


def sum_image_values_on_mask(image, mask_image):
    sum_zeros = 0
    sum_ones = 0

    mask_shape = list(mask_image.shape)
    for i in range(0, mask_shape[0]):
        for j in range(0, mask_shape[1]):
            if mask_image[i, j] == 0:
                sum_zeros += image[i, j]
            else:
                sum_ones += image[i, j]
    return [sum_zeros, sum_ones]


# TODO global counter where this function makes return
def check_item_on_edge(image, mask):
    image = np.uint8(image)
    max_image_val = np.max(image)
    e_image = np.pad(image, [(1, 1), (1, 1)], mode='constant', constant_values=0)
    e_image_shape = list(e_image.shape)

    # Max val is on border or next to border
    idx_max_val = np.unravel_index(np.argmax(e_image), e_image.shape)
    if mask.e_bordered_mask[idx_max_val] == 0:
        # Using only the closest tactile, when using 2 detection can be as far as 5cm from edge
        return True

    # Whole item inside of table
    # section not includes enough confidence and it works better withoit it
    # potentially_on_edge = False
    # for i in range(1, e_image_shape[0] - 1):
    #     for j in range(1, e_image_shape[1] - 1):
    #         if mask.e_bordered_mask[i, j] == 0 and e_image[i, j] > max_image_val / 10.0 and e_image[i, j] > 5:
    #             # Bordered mask must be used, because normal mask is used to trimming image
    #             potentially_on_edge = True
    # if not potentially_on_edge:
    #     return False

    # Check by finding centroid and distance to border
    s_image = stretch_image(image, 1.5, 2.5)
    s_centroid_point = get_image_centroid(s_image, float)
    hist = get_histogram_of_weight_from_point(s_image, s_centroid_point)
    peak = find_histogram_peak(hist, False)
    dist_to_border = get_distance_to_mask(mask.getStretchedMask(), s_centroid_point)

    # TODO whin histogram is wide it might mean that item is big and anyway will be close to the edge
    # filter out such items as in the center

    # Object close to border
    if dist_to_border < 5.0:
        return True

    # Edge of item is close to border
    # Peak is roughly diameter of object
    if dist_to_border <= peak + 2.0:
        return True

    # Check weight on close to border fields and compare to all weight
    [border_weight, center_weight] = sum_image_values_on_mask(e_image, mask.e_2bordered_mask)
    if border_weight >= center_weight:
        return True
    return False


def find_sides_of_table(mask_image):
    # Get last column and find first and the last '1'
    last_col = mask_image[:, -1]
    side_edges = np.argwhere(np.diff(np.r_[0, last_col, 0])).reshape(-1, 2)
    if len(side_edges) > 1:
        debug(DBGLevel.WARN, "Table have some border inconsistency")
    edge = side_edges[0]
    edge[1] -= 1

    # Bigger it up a little
    edge[0] += 1
    edge[1] -= 1
    return edge


def recognise_position(image, image_mask, field_size):
    # field size = [1.5, 2.5]
    mask = ImageMask()

    # Prepare useful data and prepare images
    s_image = stretch_image(image, field_size[0], field_size[1])  # Image stretched to real dimentions in cm
    # s_image_mask = stretch_image(image_mask, field_size[0], field_size[1])
    s_image_mask = mask.getStretchedMask()  # Image mask stretched to real dimentions in cm
    s_side_edges = find_sides_of_table(s_image_mask)  # Find right and left side of the table

    # Position recognition
    is_border = check_item_on_edge(image, mask)
    s_centroid_point = get_image_centroid(s_image, int)
    hist = get_histogram_of_weight_from_point(s_image, s_centroid_point)
    peak = find_histogram_peak(hist)

    # Return result
    if is_border:
        return ItemPlacement.edge
    else:
        if s_centroid_point[1] < s_side_edges[0] or s_centroid_point[1] > s_side_edges[1]:
            return ItemPlacement.side
        else:
            return ItemPlacement.center
    # return ItemPlacement.unknown
