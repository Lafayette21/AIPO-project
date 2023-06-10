from tkinter import Tk, Button, messagebox

import tkintermapview
from tkintermapview.canvas_position_marker import CanvasPositionMarker

from src.model.point import Point
from src.model.point_constats import point_constants


class MapViewer:
    INITIALIZATION_POINT: Point = point_constants["Cracow"]

    map_widget: tkintermapview.TkinterMapView

    begin_marker: CanvasPositionMarker
    end_marker: CanvasPositionMarker
    number_of_markers: int = 0

    def __init__(self, root: Tk):
        self.root = root

    def initialise(self) -> None:
        self.__initialize_map_widget()

        find_navigation_button = Button(self.root, text="Navigate", command=self.create_route)
        find_navigation_button.grid(row=0, column=0)

        clear_markers_button = Button(self.root, text="Clear markers", command=self.clear_all_markers)
        clear_markers_button.grid(row=1, column=0)

    def __initialize_map_widget(self):
        self.map_widget = tkintermapview.TkinterMapView(self.root,
                                                        width=self.__get_90_percent_of(self.root.winfo_width()),
                                                        height=self.__get_90_percent_of(self.root.winfo_height()))
        self.map_widget.set_position(self.INITIALIZATION_POINT.x, self.INITIALIZATION_POINT.y)
        self.map_widget.add_right_click_menu_command(label="Add begin marker", command=self.set_begin_marker,
                                                     pass_coords=True)
        self.map_widget.grid(row=0, column=1, rowspan=10)

    @staticmethod
    def __get_90_percent_of(value: int) -> int:
        return int(0.9 * value)

    def clear_all_markers(self) -> None:
        self.number_of_markers = 0
        self.map_widget.delete_all_marker()
        self.map_widget.add_right_click_menu_command(label="Add begin marker", command=self.set_begin_marker,
                                                     pass_coords=True)

    def set_begin_marker(self, coords):
        print("Add begin marker:", coords)
        self.begin_marker = self.map_widget.set_marker(coords[0], coords[1], text="Begin marker")
        self.number_of_markers += 1
        self.map_widget.right_click_menu_commands.clear()
        self.map_widget.add_right_click_menu_command(label="Add end marker", command=self.set_end_marker,
                                                     pass_coords=True)

    def set_end_marker(self, coords):
        print("Add end marker:", coords)
        self.end_marker = self.map_widget.set_marker(coords[0], coords[1], text="End marker")
        self.number_of_markers += 1
        self.map_widget.right_click_menu_commands.clear()

    def create_route(self):
        if self.number_of_markers != 2:
            messagebox.showerror(title="Error", message="You have not selected both points for creating navigation")
        else:
            # TODO Here implement the login for creating route between two points
            print("Success")