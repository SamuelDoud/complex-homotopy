import math
import cmath

class PointGrid(object):
    """Point Grid holds all the points on the graph and their associations"""
    def __init__(self):
        self.lines =[]
        self.current_display = []
    def addLine(self, line):
        self.lines.append(line)

    def increment(self):
        """Take every point in every line and increment them... take these incremented points and """
        for index, line in enumerate(lines): #go through each line in lines
            self.current_display[index] = [point for point in line] #list comp to update this particular line

    def displayNewPoints(self): #user calls this function to get the points that need to be displayed
        self.increment
        return current_display

    def provideFunction(self,function,n):
        """Give a complex function to this function.
        Then, operate on each point by the function
        (1-(t/n))point + (t/n)*f(point) where t is the step in the function"""
        for line in lines:
            for point in line:
                z = complex(point.real, point.imag) #z being used as the cannoical complex number
