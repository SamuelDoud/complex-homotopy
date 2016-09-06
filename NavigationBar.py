import tkinter
import matplotlib
from matplotlib.backends.backend_tkagg import NavigationToolbar2TkAgg

class NavigationBar(NavigationToolbar2TkAgg):
    """This class removes the buttons not usable in the program"""
    def __init__(self, canvas, window):
        self.toolitems = [tool for tool in NavigationToolbar2TkAgg.toolitems if tool[0] in ('Pan', 'Save')]
        self.toolitems.reverse()
        NavigationToolbar2TkAgg.__init__(self, canvas, window)
