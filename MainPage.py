from tkinter import Frame, Tk, Checkbutton, Button, Label, Entry, Toplevel, IntVar
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import PointGrid
import PlotWindow
import ComplexFunction as func

#constants for checkboxes
ON = 1
OFF = 0

class CircleBuilderPopup(object):
    """
    Class that launches a popup and collects user data to pass data back to the main window
    to build a circle.
    """
    def __init__(self, master):
        """
        Establish the GUI of this popup
        """
        self.top = Toplevel(master)
        self.circle_tuple = (0, 0)
        self.radius = Label(self.top, text="Radius")
        self.radius_entry = Entry(self.top, bd=5)
        self.center = Label(self.top, text="Center")
        self.center_entry = Entry(self.top, bd=5)
        self.build_circle_submit = Button(self.top, text="Build!", command=self.cleanup)
        self.radius.grid(row=0, column=0)
        self.radius_entry.grid(row=0, column=1)
        self.center.grid(row=1, column=0)
        self.center_entry.grid(row=1, column=1)
        self.build_circle_submit.grid(row=2, column=0, columnspan=2)
        self.top_left = 0
        self.bottom_right = 0

    def cleanup(self):
        """
        Collect the data from the user and package it into object variables, then close.
        """
        center = complex(0, 0)
        if self.center_entry.get():
            center = complex(self.center_entry.get())
        self.circle_tuple = (float(self.radius_entry.get()), center)
        self.top.destroy()

class GridBuilderPopup(object):
    """
    Class that launches a popup and collects user data to pass data back to the main window
    to build a grid.
    """
    def __init__(self, master):
        """
        Establish the GUI of this popup
        """
        self.top = Toplevel(master)
        self.top_left = complex(0, 0)
        self.bottom_right = complex(0, 0)
        self.lines = 0
        self.top_left_label = Label(self.top, text="\"Top Left\"")
        self.top_left_entry = Entry(self.top, bd=5)
        self.bottom_right_label = Label(self.top, text="\"Bottom Right\"")
        self.bottom_right_entry = Entry(self.top, bd=5)
        self.resolution_label = Label(self.top, text="Lines")
        self.resolution_entry = Entry(self.top, bd=5)
        self.build_grid_submit = Button(self.top, text="Build!", command=self.cleanup)
        self.top_left_label.grid(row=0, column=0)
        self.top_left_entry.grid(row=0, column=1)
        self.bottom_right_label.grid(row=1, column=0)
        self.bottom_right_entry.grid(row=1, column=1)
        self.resolution_label.grid(row=2, column=0)
        self.resolution_entry.grid(row=2, column=1)
        self.build_grid_submit.grid(row=3, column=0, columnspan=2)

    def cleanup(self):
        """
        Collect the data from the user and package it into object variables, then close.
        """
        if self.resolution_entry.get().isnumeric():
            self.lines = int(self.resolution_entry.get())
        self.top_left = complex(self.top_left_entry.get())
        self.bottom_right = complex(self.bottom_right_entry.get())
        #If these conditions are true then we do not have a grid
        if (self.top_left.real > self.bottom_right.real
                or self.bottom_right.imag > self.top_left.imag or self.lines == 0):
            self.bottom_right = self.top_left = complex(0, 0)
            self.lines = 0
        self.top.destroy()

class Application(Frame):
    """
    This is the window that displays the homotopy. Also it provides an interface for the user to
    manipulate the homotopy as they see fit.
    """
    def __init__(self, master=None):
        """
        A generic init function. Creates some class variables for later use.
        Calls on the function to create widgets and eventually, launches the window.
        """
        Frame.__init__(self, master)
        ROOT.title("Complex Homotopy")
        #bind the return key to the launch function
        #analogous to hitting the submit button
        ROOT.bind("<Return>", self.launch_return_key)
        #how long between frames in milliseconds
        self.default_interval = 15
        self.id_number_counter = 0
        self.line_collection = []
        self.canvas = None
        self.identity = "z"
        self.identity_function = func.ComplexFunction(self.identity)
        #self.pack()
        self.master = master
        self.point_grid = PointGrid.PointGrid()
        self.outlier_remover = IntVar()
        self.outlier_remover.set(0)
        self.reverse_checkbox_var = IntVar()
        self.reverse_checkbox_var.set(0)
        self.create_widgets()
        self.pack_widgets()
        self.animating_already = False
        self.already_paused = False
        self.popup_window = None
        self.build_sample()
        #show the graph
        self.launch()

    def create_widgets(self):
        """
        Creates and arranges the GUI.
        """
        common_bd = 5
        #checkbox to control outlier logic
        self.outlier_remover_checkbox = Checkbutton(ROOT, text="Remove outliers",
                                                    variable=self.outlier_remover,
                                                    onvalue=ON, offvalue=OFF, height=1, width=12)
        self.reverse_checkbox = Checkbutton(ROOT, text="Reverse",
                                            variable=self.reverse_checkbox_var,
                                            onvalue=ON, offvalue=OFF, height=1, width=6)
        self.pop_from_collection = Button(ROOT, text="Remove last",
                                          command=self.remove_from_collection)
        self.submit = Button(ROOT, text="Submit", command=self.launch)
        self.function_label = Label(ROOT, text="Enter a f(z)")
        self.save_video = Button(ROOT, text="Save as Video", command=self.save_video_handler)
        self.remove_front = Button(ROOT, text="Remove first", command=self.remove_first)
        self.n_label = Label(ROOT, text="Number of steps")
        self.real_max_label = Label(ROOT, text="Real max")
        self.real_min_label = Label(ROOT, text="Real min")
        self.imag_max_label = Label(ROOT, text="Imag max")
        self.imag_min_label = Label(ROOT, text="Imag min")
        self.real_max_entry = Entry(ROOT, bd=common_bd)
        self.real_min_entry = Entry(ROOT, bd=common_bd)
        self.imag_min_entry = Entry(ROOT, bd=common_bd)
        self.imag_max_entry = Entry(ROOT, bd=common_bd)
        self.function_entry = Entry(ROOT, bd=common_bd)
        self.n_entry = Entry(ROOT, bd=common_bd)
        self.circle_launcher = Button(ROOT, command=self.circle_popup, text="Circle Builder")
        self.grid_launcher = Button(ROOT, command=self.grid_popup, text="Grid Builder")

    def pack_widgets(self):
        """
        Method to pack widgets created in above method onto the window.
        This method only exists for organization purposes.
        Pythonically, this code is probably bad. I am referencing variables that are created
        outside of this method but not in the __init__ method.
        """
        #WTF tab ordering
        self.function_label.grid(row=2, column=0)
        self.function_entry.grid(row=2, column=1)
        self.n_label.grid(row=3, column=0)
        self.n_entry.grid(row=3, column=1)
        self.circle_launcher.grid(row=5, column=0)
        self.grid_launcher.grid(row=5, column=1)
        self.submit.grid(row=5, column=2)
        self.outlier_remover_checkbox.grid(row=5, column=3)
        self.reverse_checkbox.grid(row=6, column=3)
        self.remove_front.grid(row=6, column=0)
        self.pop_from_collection.grid(row=6, column=1)
        self.save_video.grid(row=6, column=2)
        self.real_max_label.grid(row=2, column=2)
        self.real_max_entry.grid(row=2, column=3)
        self.real_min_label.grid(row=2, column=5)
        self.real_min_entry.grid(row=2, column=4)
        self.imag_max_label.grid(row=3, column=2)
        self.imag_max_entry.grid(row=3, column=3)
        self.imag_min_label.grid(row=3, column=5)
        self.imag_min_entry.grid(row=3, column=4)

    def add_to_collection(self, lines):
        """
        Adds a set of lines to the collection and appends a id tag
        """
        self.line_collection.append((lines, self.id_number_counter))
        #increment the id tag
        self.id_number_counter += 1
        #return the id tag less one (as to refer to this object)
        return self.id_number_counter - 1

    def remove_from_collection(self, id_number=None):
        """
        Removes a line collection from the list. If no index is passed, the collection is
        treated like a stack
        """
        #search for the line
        #This is an ordered set. Using a binary search
        #did the user pass a value for id_number?
        if id_number:
            try:
                length = len(self.line_collection)
                index = length // 2
                last_index = index + 1
                #how much to move the index by every step
                delta = index // 2 + 1
                while self.line_collection[index][1] != id_number:
                    if self.line_collection[index][1] > id_number:
                        index -= delta
                    else:
                        index += delta
                    if last_index == index:
                        return False
                    last_index = index
                    delta //= 2
                self.line_collection.pop(index)
                #redraw
                self.point_grid.new_lines(self.flattend_lines())
                return True
            except IndexError:
                return False
        else:
            if self.line_collection:
                self.line_collection.pop()
                self.point_grid.new_lines(self.flattend_lines())
                return True
            else:
                return False

    def remove_first(self):
        """
        Take the first item on the collection and remove it.
        Then recalculate the graph.
        """
        self.line_collection.pop(0)
        self.point_grid.new_lines(self.flattend_lines())

    def build_sample(self):
        """
        A sampler method to test adding and removing shapes.
        """
        self.add_lines(self.point_grid.circle(1, complex(1, 1)))
        self.add_lines(self.point_grid.grid_lines(complex(-1, 1), complex(1, -1), 10, 10))

    def flattend_lines(self):
        """
        The collection of lines is a list of tuples with
        each tuple containing a list of lines and an id.
        This method takes all the lines in the collection
        and returns them as one list.
        """
        stripped_of_id = [line[0] for line in self.line_collection]
        return [item for sublist in stripped_of_id for item in sublist]

    def add_lines(self, list_of_lines):
        """
        Given a list of lines, add them to the Plot.
        """
        if not isinstance(list_of_lines, list):
            list_of_lines = [list_of_lines]
        for line in list_of_lines:
            self.point_grid.add_line(line)
        self.point_grid.changed_flag_unhandled = True
        return self.add_to_collection(list_of_lines)

    def build_circle(self, radius, center=complex(0, 0)):
        """
        Build a circle from a popup
        """
        return self.add_lines(self.point_grid.circle(radius, center))

    def build_grid(self, upper_right, lower_left, lines_num):
        """
        Build a grid from a popup.
        """
        return self.add_lines(self.point_grid.grid_lines(upper_right,
                                                         lower_left, lines_num, lines_num))

    def save_video_handler(self):
        """
        Dispatches the Plot to save the video.
        Should implement a filename prompt.
        """
        #now actually save the graph
        self.plot_object.save(video=True)

    def launch_return_key(self, entry):
        """
        THis is the path if hte user presses the entry key.
        Since binding sends an entry, this is a way to deal with that and reuse the
        launch method below
        """
        self.launch()

    def launch(self):
        """
        Create a new animation based on the data given by the user.
        This method will be called on the press of the submit button.
        """
        #take the input from the user.. if its null, set ito the identity function
        self.point_grid.set_user_limits(self.fetch_limits())
        if self.function_entry.get():
            function_objects = []
            function_strings = str(self.function_entry.get()).split(';') #split by the semi-colon
            for function_string in function_strings:
                #add each passed string to the list of functions
                try:
                    #check if the fuction is valid
                    function_object = func.ComplexFunction(function_string.strip())
                except Exception:
                    #fallback to the identity function
                    function_object = self.identity_function
                #add the user or identity function to the function stack
                function_objects.append(function_object)
        else:
            #fallback to identity if no string is provided
            function_objects = [self.identity_function]
        try:
            #see if the user supplied a number of steps.
            steps_from_user = int(self.n_entry.get())
        except Exception:
            steps_from_user = 1 #no animation
        #get tif the user has check the animation box
        reverse = self.reverse_checkbox_var.get() == ON
        self.point_grid.provide_function(function_objects, steps_from_user, self.flattend_lines(),
                                         reverse=reverse)
        #code for if this is the initial run of the launch method
        if not self.animating_already:
            self.plot_object = PlotWindow.PlotWindow(self.point_grid)
        self.update_graph()
        #allows the color computation to deal with if the animation is reversing
        self.plot_object.reverse = reverse
        #set the animation to the beginning
        self.plot_object.frame_number = 0
        #set the boolean that controls the outlier operation in the pointgrid to that of the user
        self.plot_object.grid.remove_outliers = self.outlier_remover.get() == ON
        self.plot_object.new_limits()

    def fetch_limits(self):
        """
        Get the limits the user put into the GUI.
        Apply logical checking (maxes must be greater than mins...
        Also insert Nones for blanks or invalid entries
        Limits arranged in a tuple as follows:
        (Real max, real min, imaginary max, imaginary min)
        """
        real_max = self.get_limit_from_entry(self.real_max_entry)
        real_min = self.get_limit_from_entry(self.real_min_entry)
        imag_max = self.get_limit_from_entry(self.imag_max_entry)
        imag_min = self.get_limit_from_entry(self.imag_min_entry)
        all_clear = True
        limits = (real_max, real_min, imag_max, imag_min)
        if None in limits:
            all_clear = False
        else:
            if real_max <= real_min or imag_max <= imag_min:
                all_clear = False
        if all_clear:
            return limits
        else:
            return (None, None, None, None)

    def get_limit_from_entry(self, limit_entry):
        """
        Given a limit entry, determine its value if it is a number.
        """
        #this variable acts as the sign of the user data
        multiplier = 1
        limit_entry_string = str(limit_entry.get())
        #replace the FIRST negative sign seen
        is_there_a_negative_sign = limit_entry_string.replace("-", "", 1)
        if is_there_a_negative_sign is not limit_entry_string:
            #the user gave a negative sign, but we had to remove it
            multiplier = -1
        #check if the use passed something legal
        if not is_there_a_negative_sign.isnumeric():
            return None
        else:
            #return the numeric value of the user data multiplied by its sign
            return float(is_there_a_negative_sign)*multiplier

    def update_graph(self):
        """
        Create the frame on which the matplotlib figure will be displayed.
        Also, kick off the animation.
        """
        self.canvas = FigureCanvasTkAgg(self.plot_object.fig, master=ROOT)
        self.plot_object.fig.canvas.mpl_connect('button_press_event', self.plot_object.toggle_pause)
        #self.canvas.show()
        self.canvas.get_tk_widget().grid(row=0, column=0, columnspan=6)
        #self.canvas.get_tk_widget().pack(side=BOTTOM, fill=BOTH, expand=True)
        self.animating_already = True
        self.plot_object.animate(interval_length=self.default_interval)

    def circle_popup(self):
        """
        Launch the circle popup window
        then buil the circle
        """
        self.popup_open()
        self.popup_window = CircleBuilderPopup(self.master)
        self.master.wait_window(self.popup_window.top)
        try:
            self.build_circle(self.popup_window.circle_tuple[0], self.popup_window.circle_tuple[1])
            self.launch()
        except AttributeError:
            print("no data")
        self.popup_close()

    def grid_popup(self):
        """
        launch a pop-up window to build a user-defined grid
        then build the grid
        """
        self.popup_open()
        self.popup_window = GridBuilderPopup(self.master)
        self.master.wait_window(self.popup_window.top)
        try:
            self.build_grid(self.popup_window.top_left, self.popup_window.bottom_right,
                            self.popup_window.lines)
            self.launch()
        except AttributeError:
            print("no data")
        self.popup_close()

    def popup_open(self):
        """
        Checks and stores if the animation is paused, then pauses the animation
        """
        self.already_paused = False
        if not self.plot_object.pause:
            self.plot_object.pause_animation()
        else:
            self.already_paused = True

    def popup_close(self):
        """
        Resumes the animation if the user had the animation running before launching the popup
        """
        if not self.already_paused:
            self.plot_object.resume_animation()

ROOT = Tk()
WINDOW = Application(master=ROOT)
WINDOW.mainloop()
