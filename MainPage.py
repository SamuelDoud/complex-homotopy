from tkinter import *
import PointGrid
import plot
import function as func
from sympy import Symbol, symbols, re, im, arg, Abs, sympify

from matplotlib import pyplot as plt
from matplotlib import animation


class Application(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.pack()
        self.createWidgets()
        self.unit_square = PointGrid.PointGrid(complex(-1+1j),complex(1-1j),20,20)
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

    def say_hi(self):
        print("hi there, everyone!")

    def launch(self):
        functionObj = func.function(str(self.function_entry.get()))
        self.unit_square.provide_function(functionObj,int(self.n_entry.get()))
        plot_window=plot.plot(self.unit_square)
        plot_window.show()

root = Tk()
app = Application(master=root)
app.mainloop()
