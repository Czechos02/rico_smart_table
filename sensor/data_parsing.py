import numpy as np
from enum import Enum


class ImageCompensationMethod(Enum):
    raw_input = 0
    input_shifted_by_max_value = 1
    input_shifted_by_calibration_value = 2
    input_scaled_by_calibration_value = 3
    input_scaled_to_fixed_value_A = 4
    input_scaled_to_fixed_value_B = 5
    input_scaled_to_fixed_value_C = 6
    input_scaled_to_calibration_value_reduced_by_A = 7
    input_scaled_to_calibration_value_reduced_by_B = 8


def flatten(seq):
    out_list = []
    for element in seq:
        element_type = type(element)
        if element_type is tuple or element_type is list or element_type is np.ndarray:
            for element_in_element in flatten(element):
                out_list.append(element_in_element)
        else:
            out_list.append(element)
    return out_list


def cast_data_to_uint8(rows, columns, raw_data):
    data_uint8 = [[0 for x in range(columns)] for y in range(rows)]

    for i in range(columns):
        for j in range(rows):
            val_uint8 = int(255 - raw_data[i][j] * 255 / 4095)

            if val_uint8 > 255:
                val_uint8 = 255
            if val_uint8 < 0:
                val_uint8 = 0

            data_uint8[i][j] = val_uint8
    return data_uint8


def parse_data_to_np_image(rows, columns, raw_data):
    for i in flatten(raw_data):
        if not i <= 255:
            raw_data = cast_data_to_uint8(rows, columns, raw_data)
            break
    np_image = np.array(raw_data, dtype=np.uint8)
    return np_image


def mask_np_image(np_image, mask):
    # TODO
    pass


def compensate_raw_image(rows, columns, image_to_compensate, calibration_image,
                         compensation_method=ImageCompensationMethod.input_scaled_to_calibration_value_reduced_by_A):
    compensated_image = [[0 for x in range(columns)] for y in range(rows)]

    if compensation_method == ImageCompensationMethod.input_shifted_by_max_value:
        image_max_value = max(max(image_to_compensate))
        for i in range(columns):
            for j in range(rows):
                compensated_image[i][j] = image_to_compensate[i][j] + 4095 - image_max_value

    elif compensation_method == ImageCompensationMethod.input_shifted_by_calibration_value:
        for i in range(columns):
            for j in range(rows):
                compensated_image[i][j] = image_to_compensate[i][j] + 4095 - calibration_image[i][j]

    elif compensation_method == ImageCompensationMethod.input_scaled_by_calibration_value:
        for i in range(columns):
            for j in range(rows):
                compensated_image[i][j] = image_to_compensate[i][j] * (4095 / calibration_image[i][j])

    elif compensation_method == ImageCompensationMethod.input_scaled_to_fixed_value_A \
            or compensation_method == ImageCompensationMethod.input_scaled_to_fixed_value_B \
            or compensation_method == ImageCompensationMethod.input_scaled_to_fixed_value_C:
        if compensation_method == ImageCompensationMethod.input_scaled_to_fixed_value_A:
            filter_value = 4000  # A
        elif compensation_method == ImageCompensationMethod.input_scaled_to_fixed_value_B:
            filter_value = 3950  # B
        else:
            filter_value = 3900  # C

        for i in range(columns):
            for j in range(rows):
                compensated_image[i][j] = image_to_compensate[i][j]
                if compensated_image[i][j] > filter_value:
                    compensated_image[i][j] = filter_value
                compensated_image[i][j] = int(compensated_image[i][j] * 4095 / filter_value)

    elif compensation_method == ImageCompensationMethod.input_scaled_to_calibration_value_reduced_by_A \
            or compensation_method == ImageCompensationMethod.input_scaled_to_calibration_value_reduced_by_B:
        if compensation_method == ImageCompensationMethod.input_scaled_to_calibration_value_reduced_by_A:
            mult_value = 0.99  # A
        else:
            mult_value = 0.98  # B

        for i in range(columns):
            for j in range(rows):
                compensated_image[i][j] = image_to_compensate[i][j]
                if compensated_image[i][j] > mult_value * calibration_image[i][j]:
                    compensated_image[i][j] = mult_value * calibration_image[i][j]
                compensated_image[i][j] = compensated_image[i][j] * 4095 / (mult_value * calibration_image[i][j])

    else:
        for i in range(columns):
            for j in range(rows):
                compensated_image[i][j] = image_to_compensate[i][j]
    return compensated_image
