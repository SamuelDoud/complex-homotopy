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
        self.identity = "z"
        self.identity_function = func.function(self.identity)
        self.pack()
        self.master=master
        self.grid = PointGrid.PointGrid()
        self.outlier_remover = IntVar()
        self.outlier_remover.set(0)
        self.create_widgets()
        self.animating_already = False
        self.add_lines()
        self.launch()

    def create_widgets(self):
        self.outlier_remover_check_box = Checkbutton(self, text = "Remove outliers", variable = self.outlier_remover,
                 onvalue = 1, offvalue = 0, height=5, width = 20)
        self.save_video = Button(self, text="Save as Video", command=self.save_video_handler)
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
        self.submit = Button(self, text ="Submit", command = self.launch)
        self.submit.pack(side =BOTTOM) 
        self.QUIT = Button(self, text="Quit", fg="red", command=root.destroy)
        self.QUIT.pack(side=BOTTOM)
        self.outlier_remover_check_box.pack(side=BOTTOM)
        self.save_video.pack(side=BOTTOM)

    def add_lines(self, list_of_lines=None):
        if list_of_lines:
            map(self.grid.add_line, list_of_lines)
        else:
            self.grid.circle(1)
            self.grid.grid_lines(complex(-1,1),complex(1,-1),10,10)

    def save_video_handler(self):
        self.plot_obj.save(self.current_function, video=True)

    def launch(self):
        """
        Create a new animation based on the data given by the user.
        This method will be called on the press of the submit button.
        """
        #take the input from the user.. if its null, set ito the identity function
        self.current_function = self.function_entry.get() if self.function_entry.get() else self.identity


        try:
            functionObj = func.function(self.current_function)
        except:
            functionObj = self.identity_function #fallback to the identity 
        try:
            n = int(self.n_entry.get())
        except:
            n = 1 #no animation
        #interval cannot be changed after lauch
        self.grid.provide_function(functionObj,n)
        
        if not self.animating_already:
            self.plot_obj=plot_window.plot_window(self.grid)
            self.update_graph(self.plot_obj)
        else:
            try:
                interval = int(self.interval_entry.get())
            except ValueError:
                interval=20
            self.plot_obj.anim._interval = interval
        self.plot_obj.grid.remove_outliers = self.outlier_remover.get() == 1 #set the boolean that controls the outlier operation in the pointgrid to that of the user
        self.plot_obj.new_limits()
        #else:
        #    self.plot_obj.new_limits() #throw the new limits in on the graph
        
    def update_graph(self, f):
        self.canvas = FigureCanvasTkAgg(f.fig,master=self)
        self.canvas.show()
        self.canvas.get_tk_widget().pack(side=BOTTOM, fill=BOTH, expand=True)
        try:
            interval = int(self.interval_entry.get())
        except ValueError:
            interval=20
        self.animating_already = True
        f.animate(interval_length=interval)


root = Tk()
app = Application(master=root)
app.mainloop()
