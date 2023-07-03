from tkinter import Canvas, filedialog
from tkinter import Menu
from tkinter import Tk, Button, Frame
from tkinter.ttk import Notebook, Style

from PIL import Image, ImageTk, ImageDraw

from .mapview import MapViewer
from .navigation import Navigation
from .point import Point


class Application(Tk):
    frame2: Frame
    startPoint: Point = None
    endPoint: Point = None

    def __init__(self, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)
        self.navigation = Navigation()
        style = Style()
        style.configure('TNotebook.Tab', padding=[30, 20])

        notebook = Notebook(self)
        notebook.grid(row=0, column=0, sticky='nsew')
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.frame2 = Frame(notebook)
        self.frame2.grid(row=1, column=0, sticky='nsew')

        notebook.add(MapViewer(), text='Map')
        notebook.add(self.frame2, text='Image')

        self.frame2.columnconfigure(0, weight=1)
        self.frame2.columnconfigure(1, weight=9)
        self.frame2.rowconfigure(0, weight=1)
        self.frame2.rowconfigure(1, weight=1)
        self.frame2.rowconfigure(2, weight=1)

        self.button4 = Button(self.frame2, text='Navigate', command=self.navigate_image)
        self.button4.grid(row=0, column=0)

        self.button5 = Button(self.frame2, text="Clear", command=self.clear_all_markers_on_image)
        self.button5.grid(row=1, column=0)

        self.button6 = Button(self.frame2, text="Upload", command=self.upload_image)
        self.button6.grid(row=2, column=0)

        self.canvas = Canvas(self.frame2, width=600, height=400)
        self.canvas.grid(row=0, column=1, rowspan=3, sticky='nsew')
        self.canvas.bind("<Button-3>", self.right_click_image)
        self.image_on_canvas = None
        self.photo = None

    def navigate_image(self):
        if self.startPoint is not None and self.endPoint is not None:
            self.image_copy = self.navigation.navigate(self.original_image, self.startPoint, self.endPoint)
            self.photo = ImageTk.PhotoImage(self.image_copy)
            self.canvas.itemconfig(self.image_on_canvas, image=self.photo)
        else:
            print("Error")

    def upload_image(self):
        filepath = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.png")])
        if filepath:
            print(f"Selected file: {filepath}")
            self.original_image = Image.open(filepath)
            self.image_copy = Image.open(filepath)
            self.photo = ImageTk.PhotoImage(self.original_image)
            self.startPoint, self.endPoint = None, None
            if self.image_on_canvas:
                self.canvas.delete(self.image_on_canvas)
            self.image_on_canvas = self.canvas.create_image(0, 0, anchor="nw", image=self.photo)
        else:
            print("No file selected.")

    def right_click_image(self, event):
        x1, y1, x2, y2 = self.canvas.bbox(self.image_on_canvas)

        self.relative_x = event.x - x1
        self.relative_y = event.y - y1

        popup = Menu(self, tearoff=0)

        if self.startPoint is not None and self.endPoint is None:
            popup.add_command(label="End", command=self.set_end_marker_on_image)
        elif self.startPoint is None and self.endPoint is None:
            popup.add_command(label="Start", command=self.set_begin_marker_on_image)

        try:
            popup.tk_popup(event.x_root, event.y_root, 0)
        finally:
            popup.grab_release()

    def clear_all_markers_on_image(self) -> None:
        self.image_copy = self.original_image.copy()
        self.photo = ImageTk.PhotoImage(self.original_image)
        self.canvas.itemconfig(self.image_on_canvas, image=self.photo)
        self.startPoint, self.endPoint = None, None

    def set_begin_marker_on_image(self):
        self.startPoint = Point(self.relative_x, self.relative_y)
        print(f"Right click on the image at: {self.relative_x}, {self.relative_y}")
        radius = 10
        draw = ImageDraw.Draw(self.image_copy)
        draw.ellipse(
            (self.relative_x - radius, self.relative_y - radius, self.relative_x + radius, self.relative_y + radius),
            fill='yellow')

        self.photo = ImageTk.PhotoImage(self.image_copy)
        self.canvas.itemconfig(self.image_on_canvas, image=self.photo)

    def set_end_marker_on_image(self):
        self.endPoint = Point(self.relative_x, self.relative_y)
        print(f"Right click on the image at: {self.relative_x}, {self.relative_y}")
        radius = 10
        draw = ImageDraw.Draw(self.image_copy)
        draw.ellipse(
            (self.relative_x - radius, self.relative_y - radius, self.relative_x + radius, self.relative_y + radius),
            fill='green')

        self.photo = ImageTk.PhotoImage(self.image_copy)
        self.canvas.itemconfig(self.image_on_canvas, image=self.photo)
