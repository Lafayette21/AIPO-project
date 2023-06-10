from tkinter import Tk

from src.gui.mapview import MapViewer


def run():
    root = Tk()
    root.title("GPS application")
    root.geometry("1000x800")
    root.resizable(width=False, height=False)
    root.update()

    MapViewer(root).initialise()

    root.mainloop()
