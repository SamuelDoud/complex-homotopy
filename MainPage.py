import pickle
import threading
import os
from itertools import cycle
import math

from tkinter import (Frame, Tk, Checkbutton, Button, Label, Entry, Toplevel, IntVar,
                     Scale, END, HORIZONTAL, Menu, filedialog, messagebox, colorchooser)
import tkinter
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.backend_bases import key_press_handler

import PointGrid
import PlotWindow
import ComplexFunction as func
import ComplexPoint
import Line

#constants for checkboxes
ON = 1
OFF = 0

DATA = 0
ID = 1

def allow_constants(string_to_strip_of_constants):
    string_to_strip_of_constants = str(string_to_strip_of_constants).upper()
    pi_const_str = str(math.pi)
    e_const_str = str(math.e)
    string_to_strip_of_constants = string_to_strip_of_constants.replace("PI", pi_const_str)
    string_to_strip_of_constants = string_to_strip_of_constants.replace("E", e_const_str)
    string_to_strip_of_constants = string_to_strip_of_constants.replace("I", "j")
    string_to_strip_of_constants = string_to_strip_of_constants.replace("J", "j")
    string_to_strip_of_constants = string_to_strip_of_constants.replace("*", "")
    return string_to_strip_of_constants

def convert_to_byte_color(tuple_colors_zero_to_one):
    list_colors_zero_to_one = list(tuple_colors_zero_to_one)
    for index, color in enumerate(list_colors_zero_to_one):
        list_colors_zero_to_one[index] = int(color * 255)
    return tuple(list_colors_zero_to_one)

def convert_to_zero_to_one(tuple_three_byte_color):
    list_three_byte_color = list(tuple_three_byte_color)
    for index, color in enumerate(list_three_byte_color):
        list_three_byte_color[index] = color / 255
    return tuple(list_three_byte_color)

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
        self.width = 15
        self.bd = 3
        self.circle_tuple = (0, 0)
        self.radius = Label(self.top, text="Radius")
        self.radius_entry = Entry(self.top, width=self.width, bd=self.bd)
        self.center = Label(self.top, text="Center")
        self.center_entry = Entry(self.top, width=self.width, bd=self.bd)
        self.build_circle_submit = Button(self.top, text="Build!", command=self.cleanup)
        self.top.bind("<Return>", self.cleanup)
        self.radius.grid(row=0, column=0)
        self.radius_entry.grid(row=0, column=1)
        self.center.grid(row=1, column=0)
        self.center_entry.grid(row=1, column=1)
        self.build_circle_submit.grid(row=2, column=0, columnspan=2)
        self.top_left = 0
        self.bottom_right = 0
        self.radius_entry.focus()

    def cleanup(self, entry=None):
        """
        Collect the data from the user and package it into object variables, then close.
        """
        center = complex(0, 0)
        if self.center_entry.get():
            center = complex(allow_constants(self.center_entry.get()))
        self.circle_tuple = (float(allow_constants(self.radius_entry.get())), center)
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
        self.width = 15
        self.bd =3
        self.top_left = complex(0, 0)
        self.bottom_right = complex(0, 0)
        self.lines = 0
        self.top_left_label = Label(self.top, text="\"Top Left\"")
        self.top_left_entry = Entry(self.top, width=self.width, bd=self.bd)
        self.bottom_right_label = Label(self.top, text="\"Bottom Right\"")
        self.bottom_right_entry = Entry(self.top, width=self.width, bd=self.bd)
        self.resolution_label = Label(self.top, text="Lines")
        self.resolution_entry = Entry(self.top, width=5)
        self.build_grid_submit = Button(self.top, text="Build!", command=self.cleanup)
        self.top.bind("<Return>", self.cleanup)
        self.top_left_label.grid(row=0, column=0)
        self.top_left_entry.grid(row=0, column=1)
        self.bottom_right_label.grid(row=1, column=0)
        self.bottom_right_entry.grid(row=1, column=1)
        self.resolution_label.grid(row=2, column=0)
        self.resolution_entry.grid(row=2, column=1)
        self.build_grid_submit.grid(row=3, column=0, columnspan=2)
        self.top_left_entry.focus()

    def cleanup(self, entry=None):
        """
        Collect the data from the user and package it into object variables, then close.
        """
        if self.resolution_entry.get().isnumeric():
            self.lines = int(self.resolution_entry.get())
        self.top_left = complex(allow_constants(self.top_left_entry.get()))
        self.bottom_right = complex(allow_constants(self.bottom_right_entry.get()))
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
    def __init__(self, master):
        """
        A generic init function. Creates some class variables for later use.
        Calls on the function to create widgets and eventually, launches the window.
        """
        Frame.__init__(self, master)
        self.master = master
        self.master.title("Complex Homotopy")
        self.master.protocol("WM_DELETE_WINDOW", self.shutdown)
        #give the icon file to the GUI
        #uncoment this when I figure out pyInstaller
        self.master.iconbitmap(resource_path("icon.ico"))
        #how long between frames in milliseconds
        self.default_interval = 40
        self.animation_thread = None
        self.extensions = [("Homotopy data", ".cht"), ("All Files", "*")]
        self.default_extension = ".cht"
        self.lines_pickle_str = "lines"
        self.limits_pickle_str = "limits"
        self.id_counter_pickle_str = "id_counter"
        self.n_steps_pickle_str = "n_steps"
        self.functions_pickle_str = "functions"
        self.reverse_checkbox_pickle_str = "reverse"
        self.outlier_remover_pickle_str = "outlier"
        self.function_objects = []
        self.id_number_counter = 0
        self.line_collection = []
        self.canvas = None
        self.toolbar = None
        self.frame_slider = None
        self.identity = "z"
        self.identity_function = func.ComplexFunction(self.identity)
        self.point_grid = PointGrid.PointGrid()
        self.outlier_remover_var = IntVar()
        self.outlier_remover_var.set(0)
        self.reverse_checkbox_var = IntVar()
        self.reverse_checkbox_var.set(0)
        self.create_widgets()
        self.pack_widgets()
        self.animating_already = False
        self.already_paused = False
        self.lock_frame = False
        self.popup_window = None
        self.build_sample()
        self.menu_creation()
        self.function_entry.focus()
        #show the graph
        self.launch()

    def shutdown(self):
        """
        Closes the application
        """
        self.master.destroy()

    def key_bindings(self):
        """
        Bind the keys.
        """
        self.master.bind("<Return>", self.launch)
        self.master.bind("<Right>", self.increment_frame)
        self.master.bind("<Left>", self.decrement_frame)
        self.master.bind("<Up>", self.interval_decrease)
        self.master.bind("<Down>", self.interval_increase)
        self.master.bind("<space>", self.plot_object.toggle_pause)

    def increment_frame(self, event):
        """
        go forward one frame
        """
        self.move_frame(1)

    def decrement_frame(self, event):
        """
        Move back one frame
        """
        self.move_frame(-1)

    def move_frame(self, delta_frames):
        """
        move the animation by delta frames
        """
        if not self.lock_frame:
            self.lock_frame = True
            was_paused_flag = True
            if not self.plot_object.pause:
                self.plot_object.pause = True
                was_paused_flag = False
            self.plot_object.frame_number += delta_frames
            if was_paused_flag:
                #this will allow one frame to draw
                self.plot_object.pause_override = True
            self.plot_object.pause = was_paused_flag
            self.lock_frame = False

    def interval_increase(self, event):
        """
        Increase the interval between frames.
        """
        self.plot_object.reset_interval(10)

    def interval_decrease(self, event):
        """
        Decrease the interval between frames
        """
        self.plot_object.reset_interval(-10)

    def menu_creation(self):
        """
        Helper method to define the menu bar
        """
        self.menubar = Menu(self.master)
        self.file_menu = Menu(self.menubar, tearoff=0)
        self.edit_menu = Menu(self.menubar, tearoff=0)
        self.view_menu = Menu(self.menubar, tearoff=0)
        self.help_menu = Menu(self.menubar, tearoff=0)
        self.object_menu = Menu(self.menubar, tearoff=0)
        self.color_menu = Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="File", menu=self.file_menu)
        self.menubar.add_cascade(label="Edit", menu=self.edit_menu)
        self.menubar.add_cascade(label="View", menu=self.view_menu)
        self.menubar.add_cascade(label="Help", menu=self.help_menu)
        self.edit_menu_create()
        self.object_menu_create()
        self.color_menu_create()
        self.file_menu_create()
        self.help_menu_create()
        self.master.config(menu=self.menubar)

    def edit_menu_create(self):
        self.edit_menu.add_cascade(label="Objects", menu=self.object_menu)
        self.edit_menu.add_cascade(label="Colors", menu=self.color_menu)
        self.edit_menu.add_command(label="Preferences")

    def color_menu_create(self):
        self.color_menu.add_command(label="New start color", command=self.new_start_color)
        self.color_menu.add_command(label="New end color", command=self.new_end_color)

    def object_menu_create(self):
        self.object_menu.add_command(label="Grid", command=self.grid_popup)
        self.object_menu.add_command(label="Circle", command=self.circle_popup)
        self.object_menu.add_separator()
        self.object_menu.add_command(label="Remove First", command=self.remove_first)
        self.object_menu.add_command(label="Remove Last", command=self.remove_from_collection)
        self.object_menu.add_command(label="Remove All", command=self.master_blaster)


    def help_menu_create(self):
        self.help_menu.add_command(label="View Help", command=self.help_message_box)

    def file_menu_create(self):
        self.file_menu.add_command(label="Save", command=self.save)
        self.file_menu.add_command(label="Open", command=self.open)
        self.file_menu.add_command(label="Exit", command=self.master.quit)

    def new_end_color(self):
        new_end_color = self.new_color_selector_box(self.plot_object._end_color)
        self.plot_object.set_end_color(new_end_color)

    def new_start_color(self):
        new_start_color = self.new_color_selector_box(self.plot_object._start_color)
        self.plot_object.set_start_color(new_start_color)

    def new_color_selector_box(self, init_color=(0,0,0)):
        was_paused = self.plot_object.set_animation(PlotWindow.PAUSE)
        init_color = convert_to_byte_color(init_color)
        new_color = convert_to_zero_to_one(colorchooser.askcolor(color=init_color,
                                                            title="Pick a new color")[0])
        self.plot_object.set_animation(was_paused)
        return new_color

    def help_message_box(self):
        #pause the animation
        self.help_message_str = "Sam Doud needs to write this up"
        was_paused_state = self.plot_object.set_animation(PlotWindow.PAUSE)
        #launch the message box
        tkinter.messagebox.showinfo("Help", self.help_message_str)
        #resume the animation if it was playing
        self.plot_object.set_animation(was_paused_state)

    def save(self):
        """
        Serialize the data of the program into a pickle file defined by the user.
        """
        data_dict = self.serialize()
        #get a file name from the user
        file_name = self.save_file_dialog()
        #check if the user actually defined a file
        #(i.e. didn't exit the prompt w/o selecting a file)
        if file_name:
            with open(file_name, "wb+") as save_file:
                pickle.dump(data_dict, save_file)

    def open(self):
        """
        Method to open a file that defines a previous state of the program.
        """
        file_name = self.open_file_dialog()
        if not file_name:
            #user gave a non-existent name
            return
        with open(file_name, mode="rb") as open_file:
            pickle_data = pickle.load(open_file)
        #unpack this data in another method
        self.deserialize(pickle_data)

    def break_apart_lines(self):
        """
        Take the line_collection and get the first point in the point order of every point and
        store that in a list so it can be pickled and reassembled later.
        """
        total = []
        lines = self.line_collection
        for shape in lines:
            temp_shape_list = []
            for line in shape[DATA]:
                temp_line_list = []
                for point in line.points:
                    temp_line_list.append(point.complex)
                temp_shape_list.append(temp_line_list)
            total.append((temp_shape_list, shape[ID]))
        return total


    def master_blaster(self):
        """
        Deletes all objects on the graph
        """
        self.line_collection = []

    def bring_lines_together(self, data):
        """
        Given a set of points on a line, change them into ComplexPoint and Line objects.
        Needed as these classes cannot be pickled.
        """
        shapes_in_data = []
        for shape in data:
            temp_lines_in_shape = []
            for line in shape[DATA]:
                temp_points_on_line = []
                for points in line:
                    temp_point = ComplexPoint.ComplexPoint(points)
                    temp_points_on_line.append(temp_point)
                temp_line = Line.Line("z", temp_points_on_line[0].complex,
                                      temp_points_on_line[-1].complex,
                                      len(temp_points_on_line), temp_points_on_line)
                temp_lines_in_shape.append(temp_line)
            shapes_in_data.append((temp_lines_in_shape, shape[ID]))
        return shapes_in_data

    def serialize(self):
        """
        Method that handles packing and saving the data from the current homotopy.
        """
        #get the first function from the user. If it does not exist, defaults to "z"
        current_functions = self.point_grid.functions[0].function_str
        #if the user declared multiple functions, handle that below
        if len(self.point_grid.functions) > 1:
            functions_in_loop = ""
            for function in self.point_grid.functions[1:]:
                functions_in_loop += functions_in_loop + ";" + function.function_str
            current_functions += functions_in_loop
        n_steps = self.point_grid.n_steps
        id_counter = self.id_number_counter
        lines = self.break_apart_lines()
        reverse = self.reverse_checkbox_var.get()
        outlier = self.outlier_remover_var.get()
        #get the limits from the user if defined
        if all(self.fetch_limits()):
            limits = (self.point_grid.real_max, self.point_grid.real_min,
                      self.point_grid.imag_max, self.point_grid.imag_min)
        else:
            #the limits were not defininded by the user
            limits = (None, None, None, None)
        #pack the data 
        return {self.functions_pickle_str:current_functions, self.n_steps_pickle_str:n_steps,
                self.id_counter_pickle_str:id_counter, self.lines_pickle_str:lines,
                self.outlier_remover_pickle_str:outlier,
                self.reverse_checkbox_pickle_str:reverse, self.limits_pickle_str:limits}

    def save_file_dialog(self):
        """
        Prompts the user to choose a file name and directory to save their data to.
        """
        title = "Save homotopy as"
        file_name = filedialog.asksaveasfilename(filetypes=self.extensions,
                                             defaultextension=self.default_extension, title=title)
        return file_name

    def deserialize(self, pickle_data):
        """
        Take the data from the pickle and load it into the program.
        """
        self.set_checkbox(self.reverse_checkbox, self.reverse_checkbox_var,
                          pickle_data[self.reverse_checkbox_pickle_str])
        self.set_checkbox(self.outlier_remover_checkbox, self.outlier_remover_var,
                          pickle_data[self.reverse_checkbox_pickle_str])
        self.id_number_counter = pickle_data[self.id_counter_pickle_str]
        n_functions = pickle_data[self.functions_pickle_str].count(";") + 1
        self.set_text(self.n_entry,
                      str(int(((pickle_data[self.n_steps_pickle_str] - 1) / n_functions))))
        self.set_text(self.function_entry, pickle_data[self.functions_pickle_str])
        self.line_collection = self.bring_lines_together(pickle_data[self.lines_pickle_str])
        limits = pickle_data[self.limits_pickle_str]
        #the user had defined limits
        if any(limits):
            self.set_text(self.real_max_entry, limits[0])
            self.set_text(self.real_min_entry, limits[1])
            self.set_text(self.imag_max_entry, limits[2])
            self.set_text(self.imag_min_entry, limits[3])
        for line in self.line_collection:
            self.point_grid.add_line(line[0])
        self.point_grid.changed_flag_unhandled = True
        self.launch()
        self.plot_object.set_frame(0)
        self.plot_object.set_animation(PlotWindow.PLAY)

    def set_checkbox(self, check_box, check_box_var, value):
        """
        General method to set the value of a checkbox based on a value
        """
        if check_box_var.get() == ON:
            check_box.select()
        else:
            check_box.deselect()

    def set_text(self, entry_box, text):
        """
        General method to set a text entry based on a entry object and text.
        """
        entry_box.delete(0, END)
        entry_box.insert(0, text)

    def open_file_dialog(self):
        """
        Launches a file browser that prompts the user to select a file to load.
        """
        title = "Open homotopy data"
        file_name = filedialog.askopenfilename(filetypes=self.extensions,
                                             defaultextension=self.default_extension, title=title)
        return file_name

    def create_widgets(self):
        """
        Creates and arranges the GUI.
        """
        common_width = 5
        common_bd = 3
        #checkbox to control outlier logic
        self.outlier_remover_checkbox = Checkbutton(self.master, text="Remove outliers",
                                                    variable=self.outlier_remover_var,
                                                    onvalue=ON, offvalue=OFF, height=1, width=12)
        self.reverse_checkbox = Checkbutton(self.master, text="Reverse",
                                            variable=self.reverse_checkbox_var,
                                            onvalue=ON, offvalue=OFF, height=1, width=6)
        self.pop_from_collection = Button(self.master, text="Remove last",
                                          command=self.remove_from_collection)
        self.submit = Button(self.master, text="Submit", command=self.launch)
        self.function_label = Label(self.master, text="Enter a f(z)")
        self.save_video = Button(self.master, text="Save as Video", command=self.save_video_handler)
        self.remove_front = Button(self.master, text="Remove first", command=self.remove_first)
        self.n_label = Label(self.master, text="Number of steps")
        self.real_max_label = Label(self.master, text="Real max")
        self.real_min_label = Label(self.master, text="Real min")
        self.imag_max_label = Label(self.master, text="Imag max")
        self.imag_min_label = Label(self.master, text="Imag min")
        self.real_max_entry = Entry(self.master, width=common_width, bd=common_bd)
        self.real_min_entry = Entry(self.master, width=common_width, bd=common_bd)
        self.imag_min_entry = Entry(self.master, width=common_width, bd=common_bd)
        self.imag_max_entry = Entry(self.master, width=common_width, bd=common_bd)
        self.function_entry = Entry(self.master, width=30, bd=common_bd)
        self.n_entry = Entry(self.master, width=common_width, bd=common_bd)
        self.frame_slider = Scale(self.master, from_=0, to=1, orient=HORIZONTAL, command=self.go_to_frame)
        self.circle_launcher = Button(self.master, command=self.circle_popup, text="Circle Builder")
        self.grid_launcher = Button(self.master, command=self.grid_popup, text="Grid Builder")

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
        self.real_max_label.grid(row=3, column=6)
        self.real_max_entry.grid(row=3, column=5)
        self.real_min_label.grid(row=3, column=2)
        self.real_min_entry.grid(row=3, column=3)
        self.imag_max_label.grid(row=2, column=3)
        self.imag_max_entry.grid(row=2, column=4)
        self.imag_min_label.grid(row=4, column=3)
        self.imag_min_entry.grid(row=4, column=4)
        self.slider_row = 1
        self.slider_column = 0

    def redraw_slider(self, steps):
        """
        Need to recreate the frame slider if the number of steps change.
        All this method does is destroys the old slider, create a new one with the current number
        of steps, and then reinject it to its old spot
        """
        self.frame_slider.destroy()
        self.frame_slider = Scale(to=self.point_grid.n_steps, length=600,
                                  from_=0, orient=HORIZONTAL, command=self.go_to_frame)
        self.frame_slider.grid(row=self.slider_row, column=self.slider_column, columnspan=6)

    def go_to_frame(self, event):
        """
        Get the value from the slider if the user changes it and set the frame equal to that.
        """
        self.plot_object.frame_number = self.frame_slider.get()

    def set_slider(self, frame_number):
        """
        Take the frame number passed and set the frame slider to it
        This method is accessed by the observer in the PlotWindow.
        """
        self.frame_slider.set(frame_number)

    def add_to_collection(self, lines):
        """
        Adds a set of lines to the collection and appends a id tag
        """
        self.line_collection.append((lines, self.id_number_counter))
        #increment the id tag
        self.id_number_counter += 1
        #return the id tag less one (as to refer to this object)
        try:
            if self.plot_object.anim:
                pass
        except AttributeError:
            try:
                self.plot_object.animate()
            except AttributeError:
                pass
        return self.id_number_counter - 1

    def remove_from_collection(self, id_number=None, top=False):
        """
        Removes a line collection from the list. If no index is passed, the collection is
        treated like a stack
        """
        #search for the line
        #This is an ordered set. Using a binary search
        #did the user pass a value for id_number?
        if top:
            #user wants the first element removed
            self.line_collection.pop(0)
        else:
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
                except IndexError:
                    return False
            else:
                #user did not pass an id number. pop from top of stack
                if self.line_collection:
                    self.line_collection.pop()
                else:
                    return False
        if self.line_collection:
            self.point_grid.provide_function(self.function_objects, self.point_grid.n_steps,
                                         self.flattened_lines(),
                                         self.reverse_checkbox_var.get() == ON)
        else:
            self.plot_object.anim = None
        #start the animation back up
        return True

    def remove_first(self):
        """
        Take the first item on the collection and remove it.
        Then recalculate the graph.
        """
        self.remove_from_collection(top=True)

    def build_sample(self):
        """
        A sampler method to test adding and removing shapes.
        """
        self.add_lines(self.point_grid.circle(1, complex(1, 1)))
        self.add_lines(self.point_grid.grid_lines(complex(-1, 1), complex(1, -1), 10, 10))

    def flattened_lines(self):
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

    def launch(self, entry=None):
        """
        Create a new animation based on the data given by the user.
        This method will be called on the press of the submit button.
        """
        #take the focus off of any entry
        self.master.focus()
        #take the input from the user.. if its null, set ito the identity function
        self.point_grid.set_user_limits(self.fetch_limits())
        if self.function_entry.get():
            self.function_objects = []
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
                self.function_objects.append(function_object)
        else:
            #fallback to identity if no string is provided
            self.function_objects = [self.identity_function]
        try:
            #see if the user supplied a number of steps.
            steps_from_user = int(self.n_entry.get()) + 1
        except Exception:
            steps_from_user = 1 #no animation
        #get if the user has checked the reverse animation box
        reverse = self.reverse_checkbox_var.get() == ON
        #give the point grid its function
        self.point_grid.provide_function(self.function_objects, steps_from_user,
                                         self.flattened_lines(), reverse=reverse)
        self.redraw_slider(steps_from_user)
        #code for if this is the initial run of the launch method
        #prevents the application from launching unneeded windows
        #bind the method set_slider to the plot_object
        if not self.animating_already:
            self.plot_object = PlotWindow.PlotWindow(self.point_grid)
            self.plot_object.bind(self.set_slider)
            #space bar press controls pause/play
            #now we can bind the keys
            self.key_bindings()
            self.update_graph()
        else:
            self.plot_object.grid = self.point_grid
            #call on the animator to start at the beginning of the graph
            self.plot_object.set_frame(0)
            #pass an iterable to reorder the frames
            self.plot_object.anim.frame_seq = cycle(range(self.point_grid.n_steps))
        #allows the color computation to deal with if the animation is reversing
        self.plot_object.reverse = reverse
        #set the boolean that controls the outlier operation in the pointgrid to that of the user
        self.plot_object.grid.remove_outliers = self.outlier_remover_var.get() == ON
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
            #this is a bad implementation. Just an empty four-tuple if there are no limits
            return (None, None, None, None)

    def get_limit_from_entry(self, limit_entry):
        """
        Given a limit entry, determine its value if it is a number.
        """
        #check if the use passed something legal
        #remove any complex notation
        num = limit_entry.get().replace("j", "")
        try:
            return float(num)
        except:
            return None

    def update_graph(self):
        """
        Create the frame on which the matplotlib figure will be displayed.
        Also, kick off the animation.
        """
        self.canvas = FigureCanvasTkAgg(self.plot_object.fig, master=self.master)
        #self.toolbar = NavigationToolbar2TkAgg(self.plot_object.fig, master=self.master)
        #self.toolbar.update()
        self.plot_object.fig.canvas.mpl_connect('button_press_event', self.plot_object.toggle_pause)
        #self.canvas.show()
        self.canvas.get_tk_widget().grid(row=0, column=0, columnspan=6)
        #self.canvas.get_tk_widget().pack(side=BOTTOM, fill=BOTH, expand=True)
        self.animating_already = True
        del self.animation_thread
        self.animation_thread = threading.Thread(target=self.plot_object.animate, args=(self.default_interval,))
        self.animation_thread.start()

    def circle_popup(self):
        """
        Launch the circle popup window
        then buil the circle
        """
        was_paused = self.plot_object.set_animation(PlotWindow.PAUSE)
        self.popup_window = CircleBuilderPopup(self.master)
        #wait for this window to be closed
        self.master.wait_window(self.popup_window.top)
        try:
            self.build_circle(self.popup_window.circle_tuple[0], self.popup_window.circle_tuple[1])
            #redraw the homotopy
            self.launch()
        except AttributeError:
            print("no data")
        self.plot_object.set_animation(was_paused)

    def grid_popup(self):
        """
        launch a pop-up window to build a user-defined grid
        then build the grid
        """
        was_paused = self.plot_object.set_animation(PlotWindow.PAUSE)
        self.popup_window = GridBuilderPopup(self.master)
        self.master.wait_window(self.popup_window.top)
        try:
            self.build_grid(self.popup_window.top_left, self.popup_window.bottom_right,
                            self.popup_window.lines)
            self.launch()
        except AttributeError:
            print("no data")
        self.plot_object.set_animation(was_paused)


def resource_path(relative_path):
    """
    A function that gets the absolute path from relative. Needed for redist.
    Found from StackOverflow.
    http://stackoverflow.com/questions/7674790/bundling-data-files-with-pyinstaller-onefile
    user: Max
    """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


ROOT = Tk()
WINDOW = Application(master=ROOT)
WINDOW.mainloop()
