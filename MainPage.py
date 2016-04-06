﻿from tkinter import *
import PointGrid
import plot_window
import function as func
from sympy import Symbol, symbols, re, im, arg, Abs, sympify

from matplotlib import pyplot as plt
from matplotlib import animation

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure


class Application(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.pack()
        self.unit_square = PointGrid.PointGrid(complex(-1+1j),complex(1-1j),20,20)
        self.createWidgets()

    def createWidgets(self):
        self.hi_there = Button(self)
        self.function_label = Label( root, text="Enter a f(z)")
        self.function_entry = Entry(root, bd=20)
        self.n_label = Label(root, text="Number of steps")
        self.n_entry = Entry(root,bd=5)
        self.function_label.pack()
        self.function_entry.pack()
        self.n_label.pack()
        self.n_entry.pack()
        self.submit = Button(root, text ="Submit", command = self.launch)
        self.submit.pack(side =BOTTOM) 
        self.QUIT = Button(self, text="QUIT", fg="red", command=root.destroy)
        self.QUIT.pack(side="bottom")
        self.update_graph(plot_window.plot_window(self.unit_square).fig)

    def say_hi(self):
        print("hi there, everyone!")

    def launch(self):
        z=symbols('z',complex=True)
        functionObj = func.function(self.function_entry.get())
        self.unit_square.provide_function(functionObj,int(self.n_entry.get()))
        plot_obj=plot_window.plot_window(self.unit_square)
        plot_obj.show()
        self.update_graph(plot_obj.fig)

    def update_graph(self, f):  
        canvas = FigureCanvasTkAgg(f, self)
        canvas.show()
        canvas.get_tk_widget().pack(side=BOTTOM, fill=BOTH, expand=True)

        toolbar = NavigationToolbar2TkAgg(canvas, self)
        toolbar.update()
        canvas._tkcanvas.pack(side=TOP, fill=BOTH, expand=True)


root = Tk()
app = Application(master=root)
app.mainloop()
