import numpy as np
from matplotlib import pyplot as plt
import cv2


class Binarizer:
    def __init__(self):
        pass

    def _setup(self, image):
        self.image = image
        if self.image is None:
            raise ValueError("No image found!")
        (height, width, channels) = self.image.shape
        self.average_image_size = int(np.ceil((height + width) / 2))
        self.orig = self.image.copy()
        self.orig = cv2.cvtColor(self.orig, cv2.COLOR_BGR2RGB)
        self.grayBlurred = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)

    def find_brightest_region(self, imagePercentage=0.08):
        radius = int(np.ceil(self.average_image_size * imagePercentage) // 2 * 2 + 1)
        self.grayBlurred = cv2.GaussianBlur(self.grayBlurred, (radius, radius), 0)
        (minVal, maxVal, minLoc, maxLoc) = cv2.minMaxLoc(self.grayBlurred)
        imageWithCircle = self.orig.copy()
        cv2.circle(imageWithCircle, maxLoc, radius, (255, 0, 0), 2)
        return minVal, maxVal, imageWithCircle

    def apply_threshold(self, maxVal):
        gray = cv2.cvtColor(self.orig, cv2.COLOR_BGR2GRAY)
        (T, thresh) = cv2.threshold(gray, maxVal, 255, cv2.THRESH_BINARY)
        return thresh

    def denoise(self, thresh):
        image_cleared = np.array(thresh)
        for i in range(3):
            image_cleared = cv2.fastNlMeansDenoising(image_cleared, None, 60, 8, int(self.average_image_size * 0.01))
            image_cleared = np.where(image_cleared < 125, 0, image_cleared)
            image_cleared = np.where(image_cleared >= 125, 255, image_cleared)
        return image_cleared

    def binarize(self, image):
        self._setup(cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR))
        minVal, maxVal, imageWithCircle = self.find_brightest_region()
        thresh = self.apply_threshold(maxVal)
        binarized_image = self.denoise(thresh)
        return binarized_image


# from PIL import Image
# image = Image.open("1.jpg")
# binarizer = Binarizer()
# binarized_image = binarizer.binarize(image)
# cv2.imwrite("output.jpg", binarized_image)
