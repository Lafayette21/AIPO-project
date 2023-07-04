from tkinter import Menu, Canvas, Tk, Button, Frame, filedialog, messagebox
from tkinter.ttk import Notebook, Style

from PIL import Image, ImageTk, ImageDraw

from .mapview import MapViewer
from .navigation import Navigation
from .point import Point


class Application(Tk):
    frame2: Frame
    start_point: Point = None
    end_point: Point = None

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
        if self.start_point is not None and self.end_point is not None:
            print(f"Started navigation from {self.start_point} to {self.end_point}")
            self.image_copy = self.navigation.navigate(self.original_image, self.start_point, self.end_point)
            self.photo = ImageTk.PhotoImage(self.image_copy)
            self.canvas.itemconfig(self.image_on_canvas, image=self.photo)
        else:
            print("Both points are not set")
            messagebox.showerror("Error", "Both points are not set")

    def upload_image(self):
        filepath = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.png")])
        if filepath:
            print(f"Selected file: {filepath}")
            self.original_image = Image.open(filepath)
            self.image_copy = Image.open(filepath)
            self.photo = ImageTk.PhotoImage(self.original_image)
            self.start_point, self.end_point = None, None
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
        radius = 10
        draw = ImageDraw.Draw(self.image_copy)
        draw.ellipse(
            (self.relative_x - radius, self.relative_y - radius, self.relative_x + radius, self.relative_y + radius),
            fill='yellow')

        self.photo = ImageTk.PhotoImage(self.image_copy)
        self.canvas.itemconfig(self.image_on_canvas, image=self.photo)

    def set_end_marker_on_image(self):
        self.end_point = Point(self.relative_x, self.relative_y)
        print(f"End point set at: {self.end_point}")
        radius = 10
        draw = ImageDraw.Draw(self.image_copy)
        draw.ellipse(
            (self.relative_x - radius, self.relative_y - radius, self.relative_x + radius, self.relative_y + radius),
            fill='green')

        self.photo = ImageTk.PhotoImage(self.image_copy)
        self.canvas.itemconfig(self.image_on_canvas, image=self.photo)
