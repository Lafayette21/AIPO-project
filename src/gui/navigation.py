
import cv2
from PIL import Image, ImageDraw

from binarizer.binarizer import Binarizer


class Navigation:
    def __init__(self):
        self.binarizer = Binarizer()

    def navigate(self, image, startPoint, endPoint):
        binarized_image = self.binarizer.binarize(image)
        output_image_pil = self.convert_to_pil(binarized_image)
        
        draw = ImageDraw.Draw(output_image_pil)

        r = 10
        x, y = startPoint.x, startPoint.y
        draw.ellipse((x-r, y-r, x+r, y+r), fill='red')

        x, y = endPoint.x, endPoint.y
        draw.ellipse((x-r, y-r, x+r, y+r), fill='red')

        return output_image_pil

    def convert_to_pil(self, image):
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image_pil = Image.fromarray(image_rgb)
        return image_pil
