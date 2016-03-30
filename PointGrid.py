import math
import cmath
import Line
import pickle


class PointGrid(object):
    """Point Grid holds all the points on the graph and their associations"""
    def __init__(self):
        self.lines =[]
        self.current_display = []
    def addLine(self, line):
        self.lines.append(line)#add the new Line object to the list

    def removeLine(self, line_name):
        #line names share prefixes and gradually get more specific....
        #standard.. "LINE_TypeOfLine_setName_LineNumber"
        #if the user calls x.remove("LINE"), then all lines are removed
        #but more specific calls can be made
        for i, line in enumerate(self.lines): #take every line in the lines list and store the line into line and save to the index to i
            if line.name.startswith(line_name):#check if the Line object's name matches the deletion standard
                del self.lines[i] #if it does, delete it from the list

    def provide_function(self,function,n):
        """Give a complex function to this function.
        Then, operate on each point by the function
        (1-(t/n))point + (t/n)*f(point) where t is the step in the function 
        after this function is completed, all the points will have their homotopy computed"""
        for line in lines:
            for i in range(len(line.points)):
                line.points[i].update_points(function, n) #z being used as the cannoical complex number

    def create_animation(self, filename, function, number_of_steps, starting_lines=None, limits=(-10,10,-10,10)):
         """The creates a output of an animation based on the parameters provided.
         Write this information to a file"""
         if not starting_lines:
            self.lines=starting_lines #provides a new set of lines, if none are provided, use the old lines
         animation_data = [function,limits]
         
         self.provide_function(function, number_of_steps) #updates the points with the needed function and homotopy
         for line in self.lines:
            animation_data.append[line.info() + line.all_points_order()]#each line is a list of points which themselves are lists of their positions throughout the deformation
         data_to_save = {"function":function.text,"steps":number_of_steps, "limits":limits,"animated_lines":animation_data}
         pickle.dump(data_to_save, open(filename+"ch", "wb" ))#this serializes the data
         