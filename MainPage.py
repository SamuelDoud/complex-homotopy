import tkinter as tk
import PointGrid
import plot
import Line
import function as func
import cmath
import math
from sympy import Symbol, symbols, re, im, arg, Abs
z=symbols('z',complex=True)
functionObj = func.function(z**2)

line = Line.Line(func.function(re(z)+2j),0,(5+0j),10,20,"black")
pts = line.parameterize_points(functionObj)


ptGrid = PointGrid.PointGrid(complex(-1+1j),complex(1-1j),20)
ptGrid.provide_function(functionObj,25)

class Application(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master)
        self.pack()
        self.createWidgets()

    def createWidgets(self):
        self.hi_there = tk.Button(self)
        z=complex(1,1)
        self.hi_there["text"] = "f("+ str(z) + ")=" + str(functionObj.evaluateAt(z))
        self.hi_there["command"] = self.say_hi
        self.hi_there.pack(side="top")

        self.QUIT = tk.Button(self, text="QUIT", fg="red",
                                            command=root.destroy)
        self.QUIT.pack(side="bottom")

    def say_hi(self):
        print("hi there, everyone!")

root = tk.Tk()
app = Application(master=root)
app.mainloop()
