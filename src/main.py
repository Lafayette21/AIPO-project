from src.gui.application import Application

if __name__ == "__main__":
    app = Application()
    app.title("GPS application")
    app.geometry("1000x800")
    app.initialise()
    app.mainloop()
