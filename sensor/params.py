import cv2
import numpy as np


class Params:
    field_dim1 = 10
    field_dim2 = 20
    field_cover_dim1 = 15
    field_cover_dim2 = 25
    field_cover_area = field_cover_dim1 * field_cover_dim2


def mask_borderer(mask):
    bordered_mask = np.copy(mask)
    for i in range(1, mask.shape[0] - 1):
        for j in range(1, mask.shape[1] - 1):
            if not mask[i, j]:
                bordered_mask[i - 1, j] = 0
                bordered_mask[i, j - 1] = 0
                bordered_mask[i - 1, j - 1] = 0
                bordered_mask[i, j] = 0
                bordered_mask[i + 1, j] = 0
                bordered_mask[i, j + 1] = 0
                bordered_mask[i + 1, j + 1] = 0
                bordered_mask[i - 1, j + 1] = 0
                bordered_mask[i + 1, j - 1] = 0
            if i == 1 or j == 1 or i == mask.shape[0] - 2 or j == mask.shape[1] - 2:
                bordered_mask[i, j] = 0
    return bordered_mask


class ImageMask:
    mask = np.zeros([16, 16])
    roi_points = np.array([[0, 7], [4, 0], [11, 0], [15, 7], [15, 15], [0, 15]])
    cv2.fillPoly(mask, [roi_points], int(1))
    mask = np.rot90(mask, 3)
    mask = mask.astype(int)

    e_mask = np.pad(mask, [(1, 1), (1, 1)], mode='constant', constant_values=0)
    e_mask = e_mask.astype(int)

    e_bordered_mask = mask_borderer(e_mask)
    e_bordered_mask = e_bordered_mask.astype(int)

    e_2bordered_mask = mask_borderer(e_bordered_mask)
    e_2bordered_mask = e_2bordered_mask.astype(int)

    stretched_mask = np.zeros([24, 40])
    roi_points = np.array([[0, 10], [10, 0], [29, 0], [39, 10], [39, 23], [0, 23]])
    cv2.fillPoly(stretched_mask, [roi_points], int(1))
    stretched_mask = np.rot90(stretched_mask, 3)
    stretched_mask = stretched_mask.astype(int)

    def getMask(self):
        return self.mask

    def getEMask(self):
        return self.e_mask

    def getEMaskWithBorder(self):
        return self.e_bordered_mask

    def getEMaskWithDoubleBorder(self):
        return self.e_2bordered_mask

    def getStretchedMask(self):
        return self.stretched_mask
