class Point:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    @staticmethod
    def empty_point(self):
        self.__init__(0, 0)

    def as_tuple(self):
        return(self.x,self.y)    

    def __str__(self):
        return f"Point: x={self.x}, y={self.y}"
