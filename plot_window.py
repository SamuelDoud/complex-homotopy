import PointGrid
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.figure import Figure

REAL=0
IMAG=1

class plot_window(object):
    """This class creates the plot in which the homotopy is displayed"""
    def __init__(self,grid):
        self.grid=grid
        self.fig=plt.figure(figsize=(5,4), dpi=100)
        self.ax = plt.axes(xlim=(self.grid.real_min, self.grid.real_max),ylim=(self.grid.imag_min, self.grid.imag_max))
        self.lines = [self.ax.plot([],[],lw=self.grid.lines[line].width)[0] for line in range(self.grid.n_lines*2+2)]
        self.ax.set_xlabel("Real")
        self.ax.set_ylabel("Imaginary")    
        self.lines_at_step=[self.grid.lines_at_step(i) for i in range(self.grid.n_steps*2+2)]

    def start(self):
        """Go to the intial state"""
        return self.animate_compute(0) #Takes what would be the first frame

    def show(self):
        plt.show() #actually display the graph
    
    def save(self,name, video=False, GIF=False):
        """
        Save the homotopy as a video file or animated image file
        """
        raise NotImplementedError #need to install FFMPEG
        if video:
            anim.save(name+'.mp4', fps=30, extra_args=['-vcodec','libx264'])
        if GIF:
            raise NotImplementedError 
        
    def animate_compute(self, step):
        """
        Function that returns the lines that will be used to display this graph.
        """
        [self.lines[index].set_data(line[REAL],line[IMAG]) for index,line in enumerate(self.lines_at_step[step])] #this will actually update the graph (on the fly computation)
        #saving this data is too memory intensive for the small amount of computational power required
        return self.lines

    def animate(self,interval_length=20):
        """
        Run the animation through the parameters passed, namely the interval between frames 
        """
        self.anim = animation.FuncAnimation(self.fig, self.animate_compute, init_func=self.start,
                               frames=self.grid.n_steps*2+2, interval=interval_length, blit=True)