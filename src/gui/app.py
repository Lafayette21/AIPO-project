from tkinter import Tk

from .application import Application


def run():
    app = Application()
    app.title("GPS application")
    app.geometry("1000x800")
    app.initialise()
    app.mainloop()