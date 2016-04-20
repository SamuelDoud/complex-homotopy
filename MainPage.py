from tkinter import *
import matplotlib
from builtins import complex
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure

import PointGrid
import plot_window
import function as func

class Application(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.pack()
        self.master=master
        self.grid = PointGrid.PointGrid()
        self.create_widgets()
        self.animating_already = False
        self.add_lines()

    def create_widgets(self):
        self.function_label = Label( root, text="Enter a f(z)")
        self.function_entry = Entry(root, bd=20)
        self.n_label = Label(root, text="Number of steps")
        self.n_entry = Entry(root,bd=5)
        self.interval_label = Label(root, text="Length of interval")
        self.interval_entry = Entry(root,bd=5)
        self.function_label.pack()
        self.function_entry.pack()
        self.n_label.pack()
        self.n_entry.pack()
        self.interval_label.pack()
        self.interval_entry.pack()
        self.submit = Button(root, text ="Submit", command = self.launch)
        self.submit.pack(side =BOTTOM) 
        self.QUIT = Button(self, text="Quit", fg="red", command=root.destroy)
        self.QUIT.pack(side=BOTTOM)

    def add_lines(self, list_of_lines=None):
        if list_of_lines:
            map(self.grid.add_line, list_of_lines)
        else:
            self.grid.circle(1)
            self.grid.grid_lines(complex(-1,1),complex(1,-1),10,10)

    def launch(self):

        try:
            functionObj = func.function(self.function_entry.get())
        except:
            functionObj = func.function("z")#identity function
        try:
            n = int(self.n_entry.get())
        except:
            n = 1 #no animation
        #interval cannot be changed after lauch
        self.grid.provide_function(functionObj,int(self.n_entry.get()))
        
        if not self.animating_already:
            self.plot_obj=plot_window.plot_window(self.grid)
            self.update_graph(self.plot_obj)
        self.plot_obj.new_limits()
        #else:
        #    self.plot_obj.new_limits() #throw the new limits in on the graph
        
    def update_graph(self, f):
        self.canvas = FigureCanvasTkAgg(f.fig,master=self)
        self.canvas.show()
        self.canvas.get_tk_widget().pack(side=BOTTOM, fill=BOTH, expand=True)
        interval=20
        if int(self.interval_entry.get()):
            interval = int(self.interval_entry.get())
        self.animating_already = True
        f.animate(interval_length=interval)


root = Tk()
app = Application(master=root)
app.mainloop()
