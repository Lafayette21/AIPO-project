from tkinter import Button, messagebox, Frame

import tkintermapview
from tkintermapview.canvas_position_marker import CanvasPositionMarker

from src.gui.point import Point
from src.gui.point_constats import point_constants


class MapViewer(Frame):
    INITIALIZATION_POINT: Point = point_constants["Cracow"]

    map_widget: tkintermapview.TkinterMapView

    begin_marker: CanvasPositionMarker
    end_marker: CanvasPositionMarker
    number_of_markers: int = 0

    def __init__(self):
        super().__init__()
        self._initialise()

    def _initialise(self) -> None:
        self.__initialize_map_widget()

        find_navigation_button = Button(self, text="Navigate", command=self.create_route)
        find_navigation_button.grid(row=0, column=0)

        clear_markers_button = Button(self, text="Clear markers", command=self.clear_all_markers)
        clear_markers_button.grid(row=1, column=0)

        reset_map_button = Button(self, text='Reset map', command=self.reset_map)
        reset_map_button.grid(row=2, column=0)

    def __initialize_map_widget(self):
        self.map_widget = tkintermapview.TkinterMapView(self,
                                                        width=900,
                                                        height=600)
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

    def reset_map(self):
        print("elo")
        self.map_widget = tkintermapview.TkinterMapView(self)
        self.map_widget.set_position(self.INITIALIZATION_POINT.x, self.INITIALIZATION_POINT.y)
        self.map_widget.add_right_click_menu_command(label="Add begin marker", command=self.set_begin_marker,
                                                     pass_coords=True)
        self.map_widget.grid(row=0, column=1, rowspan=10, sticky='nsew')
