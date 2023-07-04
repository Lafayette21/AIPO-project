import cv2
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from PIL import Image, ImageDraw
from binarizer.binarizer import Binarizer
from roadsIntersectionsDetecotr.RoadsIntersectionsDetecotr import RoadsIntersectionsDetecotr

from .point import Point


class Navigation:
    POINT_RADIUS: int = 10
    debug = False

    def __init__(self):
        self.binarizer = Binarizer()

    def navigate(self, image, start_point: Point, end_point: Point):
        if self.debug:
            image.save('src/debug/original.png')
        image = self._convert_to_cv(image)
        binary_image = self.binarizer.binarize(image)
        if self.debug:
            cv2.imwrite('src/debug/binary.png', binary_image)
        _, binary_image = cv2.threshold(binary_image, 128, 1, cv2.THRESH_BINARY)
        binary_image = np.array(binary_image,  dtype=np.int32)

        detector = RoadsIntersectionsDetecotr(binary_image)
        detector.run()

        if self.debug:
            graph = detector.graph
            node_positions = nx.get_node_attributes(graph, 'pos')
            plt.figure(figsize=(8, 6))
            nx.draw(graph, pos=node_positions, with_labels=True, width=2.0, edge_color='red')
            plt.savefig('src/debug/image_graph.png')
            plt.close()

        image_to_drow = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        new_image = detector.draw_navigation(start_point.as_tuple(), end_point.as_tuple(), image_to_drow)

        output_image_pil = self._convert_to_pil(new_image)

        drawer = ImageDraw.Draw(output_image_pil)
        self._draw_point(start_point, drawer)
        self._draw_point(end_point, drawer)

        if self.debug:
            output_image_pil.save('src/debug/output.png')

        return output_image_pil

    def _convert_to_pil(self, image_cv):
        image_rgb = cv2.cvtColor(image_cv, cv2.COLOR_BGR2RGB)
        image_pil = Image.fromarray(image_rgb)
        return image_pil

    def _convert_to_cv(self, image_pil):
        return cv2.cvtColor(np.array(image_pil), cv2.COLOR_RGB2BGR)

    def _draw_point(self, point: Point, drawer: ImageDraw):
        x1 = point.x - self.POINT_RADIUS
        y1 = point.y - self.POINT_RADIUS
        x2 = point.x + self.POINT_RADIUS
        y2 = point.y + self.POINT_RADIUS
        bounding_box = [(x1, y1), (x2, y2)]
        drawer.ellipse(bounding_box, fill='red')
