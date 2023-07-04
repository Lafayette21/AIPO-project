from tkinter import Menu, Canvas, Button, Frame, messagebox

import tkintermapview
from PIL import ImageGrab
from PIL import ImageTk, ImageDraw

from .navigation import Navigation
from .point import Point
from .point_constats import point_constants


class MapViewer(Frame):
    RADIUS = 10
    INITIALIZATION_POINT: Point = point_constants["Biłgoraj"]

    map_widget: tkintermapview.TkinterMapView
    start_point: Point = None
    end_point: Point = None

    navigation: Navigation = Navigation()

    def __init__(self):
        super().__init__()
        self._initialise()

    def _initialise(self) -> None:
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=9)
        self.rowconfigure(0, weight=1)

        self.screenshot_button = Button(self, text='Make screenshot', command=self.make_screenshot)
        self.screenshot_button.grid(row=0, column=0)

        self.navigation_button = Button(self, text="Navigate", command=self.navigate_image)

        self.map_clearing_button = Button(self, text="Clear", command=self.clear_all_markers_on_image)

        self.map_reset_button = Button(self, text="Reset map", command=self.reset_map)

        self.canvas = Canvas(self, width=900, height=600)
        self.canvas.grid(row=0, column=1, rowspan=3, sticky='nsew')
        self.canvas.bind("<Button-3>", self.right_click_image)
        self.image_on_canvas = None
        self.photo = None

        self.map_widget = tkintermapview.TkinterMapView(self)
        self.map_widget.set_position(self.INITIALIZATION_POINT.x, self.INITIALIZATION_POINT.y)
        self.map_widget.grid(row=0, column=1, rowspan=10, sticky='nsew')

    def make_screenshot(self):
        zoomed = -0.2
        self.map_widget.set_zoom(self.map_widget.zoom + zoomed)
        self.after(2000, self.capture_screenshot)

    def capture_screenshot(self):
        x = self.map_widget.winfo_rootx()
        y = self.map_widget.winfo_rooty()
        x1 = x + self.map_widget.winfo_width()
        y1 = y + self.map_widget.winfo_height()

        padding = 50

        screenshot = ImageGrab.grab((x + padding, y + padding, x1 - padding, y1 - padding))

        self.map_widget.grid_forget()

        self.photo = ImageTk.PhotoImage(screenshot)

        if self.image_on_canvas:
            self.canvas.delete(self.image_on_canvas)

        self.original_image = screenshot.copy()
        self.image_copy = screenshot.copy()

        self.image_on_canvas = self.canvas.create_image(0, 0, anchor="nw", image=self.photo)

        self.screenshot_button.grid_forget()

        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)

        self.navigation_button.grid(row=0, column=0)
        self.map_clearing_button.grid(row=1, column=0)
        self.map_reset_button.grid(row=2, column=0)

    def reset_map(self):
        print(f"Map restored to default position: {self.INITIALIZATION_POINT}")
        self.map_widget = tkintermapview.TkinterMapView(self)
        self.map_widget.set_position(self.INITIALIZATION_POINT.x, self.INITIALIZATION_POINT.y)
        self.map_widget.grid(row=0, column=1, rowspan=10, sticky='nsew')

        self.navigation_button.grid_forget()
        self.map_clearing_button.grid_forget()
        self.map_reset_button.grid_forget()

        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=0)
        self.rowconfigure(2, weight=0)

        self.screenshot_button.grid(row=0, column=0)
        self.start_point, self.end_point = None, None

    def right_click_image(self, event):
        x1, y1, x2, y2 = self.canvas.bbox(self.image_on_canvas)

        self.relative_x = event.x - x1
        self.relative_y = event.y - y1

        popup = Menu(self, tearoff=0)

        if self.start_point is not None and self.end_point is None:
            popup.add_command(label="End", command=self.set_end_marker_on_image)
        elif self.start_point is None and self.end_point is None:
            popup.add_command(label="Start", command=self.set_begin_marker_on_image)

        try:
            popup.tk_popup(event.x_root, event.y_root, 0)
        finally:
            popup.grab_release()

    def clear_all_markers_on_image(self) -> None:
        print("All markers cleared")
        self.image_copy = self.original_image.copy()
        self.photo = ImageTk.PhotoImage(self.original_image)
        self.canvas.itemconfig(self.image_on_canvas, image=self.photo)
        self.start_point, self.end_point = None, None

    def set_begin_marker_on_image(self):
        self.start_point = Point(self.relative_x, self.relative_y)
        print(f"Start point set at: {self.start_point}")
        draw = ImageDraw.Draw(self.image_copy)
        draw.ellipse(
            (self.relative_x - self.RADIUS, self.relative_y - self.RADIUS, self.relative_x + self.RADIUS,
             self.relative_y + self.RADIUS),
            fill='yellow')

        self.photo = ImageTk.PhotoImage(self.image_copy)
        self.canvas.itemconfig(self.image_on_canvas, image=self.photo)

    def set_end_marker_on_image(self):
        self.end_point = Point(self.relative_x, self.relative_y)
        print(f"End point set at: {self.end_point}")
        draw = ImageDraw.Draw(self.image_copy)
        draw.ellipse(
            (self.relative_x - self.RADIUS, self.relative_y - self.RADIUS, self.relative_x + self.RADIUS,
             self.relative_y + self.RADIUS),
            fill='green')

        self.photo = ImageTk.PhotoImage(self.image_copy)
        self.canvas.itemconfig(self.image_on_canvas, image=self.photo)

    def navigate_image(self):
        if self.start_point is not None and self.end_point is not None:
            print(f"Started navigation from {self.start_point} to {self.end_point}")
            self.image_copy = self.navigation.navigate(self.original_image, self.start_point, self.end_point)
            self.photo = ImageTk.PhotoImage(self.image_copy)
            self.canvas.itemconfig(self.image_on_canvas, image=self.photo)
        else:
            print("Both points are not set")
            messagebox.showerror("Error", "Both points are not set")
