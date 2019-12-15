import numpy as np
import cv2 as cv
from matplotlib import pyplot as plt


def stuff():
    img = cv.imread('camera/images/potato.jpg',0)
    plt.imshow(img, cmap='gray', interpolation='bicubic')
    plt.xticks([]), plt.yticks([])  # to hide tick values on X and Y axis
    plt.show()


def test():
    print("test")
