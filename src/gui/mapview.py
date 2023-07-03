from tkinter import Button, messagebox, Frame, Canvas

import tkintermapview
from PIL import ImageGrab, ImageTk

from .navigation import Navigation
from .point import Point
from .point_constats import point_constants


class MapViewer(Frame):
    INITIALIZATION_POINT: Point = point_constants["Cracow"]

    map_widget: tkintermapview.TkinterMapView
    begin_point: Point
    end_point: Point
    number_of_markers: int = 0

    navigation: Navigation = Navigation()

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
        self.map_widget = tkintermapview.TkinterMapView(self, width=900, height=600)
        self.map_widget.set_position(self.INITIALIZATION_POINT.x, self.INITIALIZATION_POINT.y)
        self.map_widget.add_right_click_menu_command(label="Add begin marker", command=self.set_begin_marker,
                                                     pass_coords=True)
        self.map_widget.grid(row=0, column=1, rowspan=10)

    @staticmethod
    def __get_90_percent_of(value: int) -> int:
        return int(0.9 * value)

    def clear_all_markers(self) -> None:
        print("All markers cleared")
        self.number_of_markers = 0
        self.map_widget.delete_all_marker()
        self.map_widget.add_right_click_menu_command(label="Add begin marker", command=self.set_begin_marker,
                                                     pass_coords=True)

    def set_begin_marker(self, coords):
        print("Add begin marker:", coords)
        self.map_widget.set_marker(coords[0], coords[1], text="Begin marker")
        self.begin_point = Point(*coords)
        self.number_of_markers += 1
        self.map_widget.right_click_menu_commands.clear()
        self.map_widget.add_right_click_menu_command(label="Add end marker", command=self.set_end_marker,
                                                     pass_coords=True)

    def set_end_marker(self, coords):
        print("Add end marker:", coords)
        self.map_widget.set_marker(coords[0], coords[1], text="End marker")
        self.end_point = Point(*coords)
        self.number_of_markers += 1
        self.map_widget.right_click_menu_commands.clear()

    def create_route(self):
        if self.number_of_markers == 2:
            x = self.map_widget.winfo_rootx()
            y = self.map_widget.winfo_rooty()
            x1 = x + self.map_widget.winfo_width()
            y1 = y + self.map_widget.winfo_height()

            output_image = ImageGrab.grab().crop((x, y, x1, y1))
            output_image = self.navigation.navigate(output_image, self.begin_point, self.end_point)

            self.map_widget.grid_forget()

            output_photo = ImageTk.PhotoImage(output_image)
            canvas1 = Canvas(self, width=self.map_widget.width, height=self.map_widget.height)
            canvas1.create_image(0, 0, anchor='nw', image=output_photo)
            canvas1.grid(row=0, column=1, rowspan=10, sticky='nsew')
        else:
            messagebox.showerror(title="Error", message="You have not selected both points for creating navigation")

    def reset_map(self):
        print(f"Map is now at beginning point: {self.INITIALIZATION_POINT}")
        self.number_of_markers = 0
        self.map_widget = tkintermapview.TkinterMapView(self)
        self.map_widget.set_position(self.INITIALIZATION_POINT.x, self.INITIALIZATION_POINT.y)
        self.map_widget.add_right_click_menu_command(label="Add begin marker", command=self.set_begin_marker,
                                                     pass_coords=True)
        self.map_widget.grid(row=0, column=1, rowspan=10, sticky='nsew')
