import tkinter
from tkinter import Entry, Label, Button, Toplevel, StringVar
import math

class BuilderPopup(object):
    def __init__(self, master):
        self.data = []
        self.top = Toplevel(master)
        self.width = 15
        self.bd =3

class CircleBuilderPopup(BuilderPopup):
    """
    Class that launches a popup and collects user data to pass data back to the main window
    to build a circle.
    """
    def __init__(self, master):
        """
        Establish the GUI of this popup
        """
        BuilderPopup.__init__(self, master)
        self.data = (0, 0)
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
        self.data = (float(allow_constants(self.radius_entry.get())), center)
        self.top.destroy()

class DiskBuilderPopup(BuilderPopup):
    """
    Class that launches a popup and collects user data to pass data back to the main window
    to build a circle.
    """
    def __init__(self, master):
        """
        Establish the GUI of this popup
        """
        BuilderPopup.__init__(self, master)
        self.data = (0, 0, 0)
        self.radius = Label(self.top, text="Radius")
        self.radius_entry = Entry(self.top, width=self.width, bd=self.bd)
        self.n_circles_entry = Entry(self.top, width=self.width, bd=self.bd)
        self.n_circles_label = Label(self.top, text="Number of circles")
        self.center = Label(self.top, text="Center")
        self.center_entry = Entry(self.top, width=self.width, bd=self.bd)
        self.build_circle_submit = Button(self.top, text="Build!", command=self.cleanup)
        self.top.bind("<Return>", self.cleanup)
        self.radius.grid(row=0, column=0)
        self.radius_entry.grid(row=0, column=1)
        self.n_circles_label.grid(row=1, column=0)
        self.n_circles_entry.grid(row=1, column=1)
        self.center.grid(row=2, column=0)
        self.center_entry.grid(row=2, column=1)
        self.build_circle_submit.grid(row=3, column=0, columnspan=2)
        self.top_left = 0
        self.bottom_right = 0
        self.radius_entry.focus()

    def cleanup(self, entry=None):
        """
        Collect the data from the user and package it into object variables, then close.
        """
        center = complex(0, 0)
        try:
            if self.center_entry.get():
                center = complex(allow_constants(self.center_entry.get()))
            n_circles = int(self.n_circles_entry.get())
            self.data = (float(allow_constants(self.radius_entry.get())), n_circles, center)
        except:
            pass
        self.top.destroy()

class GridBuilderPopup(BuilderPopup):
    """
    Class that launches a popup and collects user data to pass data back to the main window
    to build a grid.
    """
    def __init__(self, master):
        """
        Establish the GUI of this popup
        """
        BuilderPopup.__init__(self, master)
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
        self.data = (0, 0, 0)

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
        self.data = (self.top_left, self.bottom_right, self.lines)
        self.top.destroy()

class SpindleBuilderPopup(BuilderPopup):
    """
    Class that launches a popup and collects user data to pass data back to the main window
    to build a circle.
    """
    def __init__(self, master):
        """
        Establish the GUI of this popup
        """
        BuilderPopup.__init__(self, master)
        self.data = (0, 0, 0)
        self.radius = Label(self.top, text="Radius")
        self.radius_entry = Entry(self.top, width=self.width, bd=self.bd)
        self.n_circles_entry = Entry(self.top, width=self.width, bd=self.bd)
        self.n_circles_label = Label(self.top, text="Number of circles")
        self.center = Label(self.top, text="Center")
        self.center_entry = Entry(self.top, width=self.width, bd=self.bd)
        self.spindles = Label(self.top, text="Number of \"Roots\"")
        self.spindles_entry = Entry(self.top, width=self.width, bd=self.bd)
        self.build_spindle_submit = Button(self.top, text="Build!", command=self.cleanup)
        self.top.bind("<Return>", self.cleanup)
        self.radius.grid(row=0, column=0)
        self.radius_entry.grid(row=0, column=1)
        self.n_circles_label.grid(row=1, column=0)
        self.n_circles_entry.grid(row=1, column=1)
        self.center.grid(row=2, column=0)
        self.center_entry.grid(row=2, column=1)
        self.spindles_entry.grid(row=3, column=1)
        self.spindles.grid(row=3, column=0)
        self.build_spindle_submit.grid(row=4, column=0, columnspan=2)
        self.top_left = 0
        self.bottom_right = 0
        self.radius_entry.focus()

    def cleanup(self, entry=None):
        """
        Collect the data from the user and package it into object variables, then close.
        """
        center = complex(0, 0)
        try:
            if self.center_entry.get():
                #only ingest the center if it is passed by the user
                center = complex(allow_constants(self.center_entry.get()))
            n_circles = int(self.n_circles_entry.get())
            #this is the data that the passed builder function requires
            self.data = (int(self.spindles_entry.get()), 
                         float(allow_constants(self.radius_entry.get())), n_circles, center)
        except Exception:
            #Invalid entry data... eventually log this
            pass
        self.top.destroy()

def allow_constants(string_to_strip_of_constants):
    """Allows a user to enter certain constants in various ways"""
    #applies arithmetic to a string such as 3pi so that a computer can understand it
    string_to_strip_of_constants = str(string_to_strip_of_constants).upper()
    pi_const_str = str(math.pi)
    e_const_str = str(math.e)
    string_to_strip_of_constants = string_to_strip_of_constants.replace("PI", pi_const_str)
    string_to_strip_of_constants = string_to_strip_of_constants.replace("E", e_const_str)
    string_to_strip_of_constants = string_to_strip_of_constants.replace("I", "j")
    string_to_strip_of_constants = string_to_strip_of_constants.replace("J", "j")
    string_to_strip_of_constants = string_to_strip_of_constants.replace("*", "")
    return string_to_strip_of_constants
