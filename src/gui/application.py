from tkinter import Tk, Button, messagebox, Frame, Label, PhotoImage
from tkinter.ttk import Notebook, Style
import tkintermapview
from tkintermapview.canvas_position_marker import CanvasPositionMarker
from .point import Point
from .point_constats import point_constants
from .navigation import Navigation
from tkinter import filedialog
from PIL import Image, ImageTk
from PIL import ImageDraw
from tkinter import Canvas, filedialog
from PIL import Image, ImageTk, ImageDraw
from tkinter import Menu
from PIL import ImageGrab

class Application(Tk):
    map_widget: tkintermapview.TkinterMapView
    INITIALIZATION_POINT: Point = point_constants["Cracow"]
    frame1: Frame 
    frame2: Frame
    begin_marker: CanvasPositionMarker
    end_marker: CanvasPositionMarker
    number_of_markers: int = 0
    startPoint: Point = None
    endPoint: Point = None

    def __init__(self, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)
        self.navigation = Navigation()
        style = Style()
        self.resizable(width=True, height=True)
        self.geometry("1000x500")
        style.configure('TNotebook.Tab', padding=[30, 20])

        notebook = Notebook(self)
        notebook.grid(row=0, column=0, sticky='nsew')
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.frame1 = Frame(notebook)
        self.frame1.grid(row=0, column=0, sticky='nsew')

        self.frame2 = Frame(notebook)
        self.frame2.grid(row=1, column=0, sticky='nsew')

        notebook.add(self.frame1, text='Map')
        notebook.add(self.frame2, text='Image')

        self.frame1.columnconfigure(0, weight=1)
        self.frame1.columnconfigure(1, weight=9)
        self.frame1.rowconfigure(0, weight=1)
        self.frame1.rowconfigure(1, weight=1)
        self.frame1.rowconfigure(2, weight=1)

        self.frame2.columnconfigure(0, weight=1)
        self.frame2.columnconfigure(1, weight=9)
        self.frame2.rowconfigure(0, weight=1)
        self.frame2.rowconfigure(1, weight=1)
        self.frame2.rowconfigure(2, weight=1)

        self.button1 = Button(self.frame1, text='Navigate', command=self.navigate_map)
        self.button1.grid(row=0, column=0)

        self.button2 = Button(self.frame1, text='Clear', command=self.clear_all_markers_on_map)
        self.button2.grid(row=1, column=0)

        self.button3 = Button(self.frame1, text='Reset map', command=self.reset_map)
        self.button3.grid(row=2, column=0)

        self.map_widget = tkintermapview.TkinterMapView(self.frame1)
        self.map_widget.set_position(self.INITIALIZATION_POINT.x, self.INITIALIZATION_POINT.y)
        self.map_widget.bind("<Button-3>", self.right_click_map)  # bind right click event to the map widget
        self.map_widget.grid(row=0, column=1, rowspan=3, sticky='nsew')

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
    def right_click_map(self, event):
        # get the pixel coordinates from the event
        print("Right click on the map at:")
        # here you can add the marker placement logic
    def reset_map(self):
        if hasattr(self, 'image_label'):
            self.image_label.grid_forget()
            del self.image_label

        self.map_widget = tkintermapview.TkinterMapView(self.frame1)
        self.map_widget.set_position(self.INITIALIZATION_POINT.x, self.INITIALIZATION_POINT.y)
        self.map_widget.add_right_click_menu_command(label="Add begin marker", command=self.set_begin_marker_on_map, pass_coords=True)
        self.map_widget.grid(row=0, column=1, rowspan=3, sticky='nsew')


    def navigate_image(self):
        if self.startPoint is not None and self.endPoint is not None:
            self.image_copy = self.navigation.navigate(self.original_image, self.startPoint, self.endPoint)
            self.photo = ImageTk.PhotoImage(self.image_copy)
            self.canvas.itemconfig(self.image_on_canvas, image=self.photo)
        else:
            print("Error")

    def navigate_map(self):
        if self.startPoint is not None and self.endPoint is not None:
            x = self.map_widget.winfo_rootx()
            y = self.map_widget.winfo_rooty()
            x1 = x + self.map_widget.winfo_width()
            y1 = y + self.map_widget.winfo_height()
            
            output_image = ImageGrab.grab().crop((x,y,x1,y1))
            output_image = self.navigation.navigate(output_image, self.startPoint, self.endPoint)

            self.map_widget.grid_forget()

            output_photo = ImageTk.PhotoImage(output_image)

            self.output_photo = output_photo

            self.canvas1 = Canvas(self.frame1)
            self.canvas1.create_image(0, 0, anchor='nw', image=self.output_photo)
            self.canvas1.grid(row=0, column=1, rowspan=3, sticky='nsew')
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
        draw.ellipse((self.relative_x-radius, self.relative_y-radius, self.relative_x+radius, self.relative_y+radius), fill='yellow')

        self.photo = ImageTk.PhotoImage(self.image_copy)
        self.canvas.itemconfig(self.image_on_canvas, image=self.photo)

    def set_end_marker_on_image(self):
        self.endPoint = Point(self.relative_x, self.relative_y)
        print(f"Right click on the image at: {self.relative_x}, {self.relative_y}")
        radius = 10 
        draw = ImageDraw.Draw(self.image_copy)
        draw.ellipse((self.relative_x-radius, self.relative_y-radius, self.relative_x+radius, self.relative_y+radius), fill='green')

        self.photo = ImageTk.PhotoImage(self.image_copy)
        self.canvas.itemconfig(self.image_on_canvas, image=self.photo)

    def clear_all_markers_on_map(self) -> None:
        self.number_of_markers = 0
        self.map_widget.delete_all_marker()
        self.map_widget.add_right_click_menu_command(label="Add begin marker", command=self.set_begin_marker_on_map, pass_coords=True)

    def set_begin_marker_on_map(self, coords):
        print("Add begin marker:", coords)
        self.startPoint = Point(*coords)
        print(f"Start point is now: {self.startPoint.x}, {self.startPoint.y}")  # added for debugging
        self.begin_marker = self.map_widget.set_marker(*coords, text="Begin marker")
        self.number_of_markers += 1
        self.map_widget.right_click_menu_commands.clear()
        self.map_widget.add_right_click_menu_command(label="Add end marker", command=self.set_end_marker_on_map,pass_coords=True)

    def set_end_marker_on_map(self, coords):
        print("Add end marker:", coords)
        self.endPoint = Point(*coords)
        print(f"End point is now: {self.endPoint.x}, {self.endPoint.y}")  # added for debugging
        self.end_marker = self.map_widget.set_marker(*coords, text="End marker")
        self.number_of_markers += 1
        self.map_widget.right_click_menu_commands.clear()

app = Application()
app.mainloop()
