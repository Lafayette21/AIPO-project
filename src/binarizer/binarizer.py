import cv2
import numpy as np


class Binarizer:
    def __init__(self):
        pass

    def _setup(self, image):
        self.image = image
        if self.image is None:
            raise ValueError("No image found!")
        (self.height, self.width, channels) = self.image.shape
        self.average_image_size = int(np.ceil((self.height + self.width) / 2))
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

    def connect_lines(self, thresh):
        lines = cv2.HoughLinesP(thresh, rho=1, theta=np.pi / 180, threshold=30,
                                minLineLength=int(self.average_image_size * 0.15),
                                maxLineGap=np.ceil((self.height + self.width) / 2 * 0.02))
        for line in lines:
            cv2.line(thresh, (line[0][0], line[0][1]), (line[0][2], line[0][3]), (255, 0, 0), 1)
        return thresh

    def fill_holes(self, bin_img):
        scale_percent = 50  # percent of original size
        width = int(bin_img.shape[1] * scale_percent / 100)
        height = int(bin_img.shape[0] * scale_percent / 100)
        dim = (width, height)

        # resize image
        filtered_img = cv2.resize(bin_img, dim, interpolation=cv2.INTER_AREA)
        dim = (bin_img.shape[1], bin_img.shape[0])
        filtered_img = cv2.resize(filtered_img, dim, interpolation=cv2.INTER_AREA)
        filtered_img = cv2.cvtColor(filtered_img, cv2.COLOR_GRAY2BGR)
        filtered_img = cv2.detailEnhance(filtered_img, sigma_s=100, sigma_r=0.1)
        filtered_img = cv2.detailEnhance(filtered_img, sigma_s=200, sigma_r=0.1)
        filtered_img = cv2.detailEnhance(filtered_img, sigma_s=200, sigma_r=1)
        filtered_img = cv2.detailEnhance(filtered_img, sigma_s=200, sigma_r=1)
        filtered_img = cv2.cvtColor(filtered_img, cv2.COLOR_BGR2GRAY)

        return filtered_img

    def dilate(self, bin_img):
        kernel = np.array([[0.25,1,0.25],
                        [1,0.25,1],
                        [0.25,1,0.25]])
        img_dilation = cv2.dilate(bin_img, kernel, iterations=1)
        return img_dilation

    def binarize(self, image):
        self._setup(image)
        minVal, maxVal, imageWithCircle = self.find_brightest_region()
        binarized_image = self.apply_threshold(maxVal)
        binarized_image = self.denoise(binarized_image)
        binarized_image = self.connect_lines(binarized_image)
        binarized_image = self.fill_holes(binarized_image)
        binarized_image = self.dilate(binarized_image)
        return binarized_image
