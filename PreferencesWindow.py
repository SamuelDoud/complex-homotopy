import tkinter
from tkinter import Entry, Label, Button, Toplevel, StringVar

class PreferencesWindow(object):
    """Launch a window to prompt the user to change settings"""
    def __init__(self, master, dict_attributes):
        self.dict_attributes = dict(dict_attributes)
        self.top = Toplevel(master)
        self.attributes = self.dict_attributes.keys()
        self.attribute_values = list(self.dict_attributes.values())
        self.entries = []
        for row, attribute in enumerate(self.attributes):
            entry_text = self.dict_attributes[attribute]
            this_label = Label(self.top, text=attribute)
            this_entry = Entry(self.top)
            this_entry.insert('0', entry_text)
            this_label.grid(row=row, column=0)
            this_entry.grid(row=row, column=1)
            self.entries.append(this_entry)
        self.submit_button = Button(self.top, text="Ok", command=self.determine_values)
        self.cancel_button = Button(self.top, text="Cancel", command=self.top.destroy)
        self.submit_button.grid(row=len(self.attribute_values), column=0)
        self.cancel_button.grid(row=len(self.attribute_values), column=1)
        self.top.bind("<Return>", self.determine_values)
        self.entries[0].focus()

    def determine_values(self, entry=None):
        for index, attribute in enumerate(self.attribute_values):
            if self.entries[index].get():
                self.attribute_values[index] = self.entries[index].get()
        self.dict_attributes = dict(zip(self.attributes, self.attribute_values))
        self.top.destroy()



