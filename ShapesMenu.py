import tkinter
from tkinter import Listbox, Toplevel, Button, ACTIVE, ANCHOR

class ShapesMenu(object):
    """
    """
    def __init__(self, master, line_collection):
        try:
            self.width_of_entry = len(line_collection[0])
        except IndexError:
            self.width_of_entry = 0
        self.top = Toplevel(master)
        self.current_lines_listbox = Listbox(self.top)
        self.removed_lines_listbox = Listbox(self.top)
        self.submit = Button(self.top, text = "Ok", command=self.submit)
        self.remove_button = Button(self.top, text = "Remove", command=self.remove_line)
        self.cancel = Button(self.top, text = "Cancel", command=self.top.destroy)
        self.top.bind("<Return>", func=self.submit)
        self.current_lines = line_collection
        self.removed_lines = []
        self.ids_internal = []
        self.ids = []
        for index, line in enumerate(self.current_lines):
            #removes the point data and converts the rest to strings
            id = line[1]
            if id not in self.ids_internal:
                self.ids_internal.append(id)
                self.ids.append(id)
                line = [str(element) for element in line[1:]]
                
                #put into the list
                self.current_lines_listbox.insert(index, " ".join(line))
        self.current_lines_listbox.grid(row=0, column=0, columnspan=3)
        self.submit.grid(row=1, column=1)
        self.cancel.grid(row=1, column=2)
        self.remove_button.grid(row=1, column=0)
        
    def submit(self):
        #expose the internal IDs to remove to the exterior methods
        self.ids = self.ids_internal
        self.top.destroy()

    def remove_line(self):
        """Take the active line and remove it"""
        
        line_to_remove = self.current_lines_listbox.get(ANCHOR)
        id_to_remove = int(line_to_remove.split(" ")[0])
        #remove it from the ID list
        self.ids_internal.remove(id_to_remove)
        #remove it from the listbox
        self.current_lines_listbox = self.current_lines_listbox.delete(ANCHOR)
