from gui.application import Application

if __name__ == "__main__":
    app = Application()
    app.title("GPS application")
    app.geometry("1024x600")
    app.resizable(width=True, height=True)
    app.mainloop()
