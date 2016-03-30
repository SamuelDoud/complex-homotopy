class Line(object):
    """description of class"""
    def __init__(self, name, points, simply_connected=False):
        self.simply_connected=simply_connected
        self.name=name
        self.points=points
        self.count=points

