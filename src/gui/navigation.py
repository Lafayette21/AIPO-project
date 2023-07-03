import cv2
from PIL import Image, ImageDraw

from binarizer.binarizer import Binarizer

from .point import Point


class Navigation:
    POINT_RADIUS: int = 10

    def __init__(self):
        self.binarizer = Binarizer()

    def navigate(self, image, start_point: Point, end_point: Point):
        binary_image = self.binarizer.binarize(image)
        output_image_pil = self._convert_to_pil(binary_image)

        drawer = ImageDraw.Draw(output_image_pil)

        self._draw_point(start_point, drawer)
        self._draw_point(start_point, drawer)

        return output_image_pil

    def _convert_to_pil(self, image):
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image_pil = Image.fromarray(image_rgb)
        return image_pil

    def _draw_point(self, point: Point, drawer: ImageDraw):
        drawer.ellipse(point.x - self.POINT_RADIUS, point.y - self.POINT_RADIUS,
                       point.x + self.POINT_RADIUS, point.y + self.POINT_RADIUS,
                       fill='red')
