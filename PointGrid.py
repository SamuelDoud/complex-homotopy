import math
import cmath
import Line

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
                
    def increment(self):
        """Take every point in every line and increment them... take these incremented points and """
        for index in range(len(self.lines)): #go through each line in lines
            self.lines[i].NextFrame()

    def NextFrame(self):
        """Calls on each line to increment its points"""
        self.increment()
        return self.lines

    def provideFunction(self,function,n):
        """Give a complex function to this function.
        Then, operate on each point by the function
        (1-(t/n))point + (t/n)*f(point) where t is the step in the function 
        after this function is completed, all the points will have their homotopy computed"""
        for line in lines:
            for i in range(len(line.points)):
                line.points[i].updatePoints(function, n) #z being used as the cannoical complex number
