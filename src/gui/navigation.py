import cv2
from PIL import Image, ImageDraw
import numpy as np

from binarizer.binarizer import Binarizer
from roadsIntersectionsDetecotr.RoadsIntersectionsDetecotr import RoadsIntersectionsDetecotr

from .point import Point


class Navigation:
    POINT_RADIUS: int = 10

    def __init__(self):
        self.binarizer = Binarizer()

    def navigate(self, image, start_point: Point, end_point: Point):
        binary_image = self.binarizer.binarize(image)
        _, binary_image = cv2.threshold(binary_image, 128, 1, cv2.THRESH_BINARY)
        binary_image = np.array(binary_image,  dtype=np.int32)
        detector = RoadsIntersectionsDetecotr(binary_image)
        detector.run()
        image_to_drow = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        new_image = detector.draw_navigation(start_point.as_tuple(), end_point.as_tuple(), image_to_drow)

        output_image_pil = self._convert_to_pil(new_image)

        drawer = ImageDraw.Draw(output_image_pil)

        self._draw_point(start_point, drawer)
        self._draw_point(end_point, drawer)

        return output_image_pil

    def _convert_to_pil(self, image):
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image_pil = Image.fromarray(image_rgb)
        return image_pil

    def _draw_point(self, point: Point, drawer: ImageDraw):
        x1 = point.x - self.POINT_RADIUS
        y1 = point.y - self.POINT_RADIUS
        x2 = point.x + self.POINT_RADIUS
        y2 = point.y + self.POINT_RADIUS
        bounding_box = [(x1, y1), (x2, y2)]
        drawer.ellipse(bounding_box, fill='red')
