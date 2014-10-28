"""
@requires: NumPy
@requires: SciPy
@requires: Pylab (at least 1.0.0)
@author: Carolin Villforth
@summary: A collection of General Useful Tools of all Trades
"""

import numpy
import scipy
import pylab
from scipy import stats
from mpl_toolkits.axes_grid1 import host_subplot
import mpl_toolkits.axisartist as AA

class AnaKDE():
    """
    A Tool for Analyzing Kernel Density Estimators (KDE)
    Interactive Plotting
    @type input: data array/KDE
    @type InData: True/False
    @type CFill: True/False
    @type PlotData: True/False
    @type levels: None/List
    @param input: Input Data, either a KDE or an array with the data.
    
    If data is input, InData needs to be set to True.
    
    If KDE is input, InData needs to be set to False.
    @param InData: Defining Data Input Type (see input)
    @param CFill: If True, filled contours will be plotted.
    
    If False, line contours will be plotted
    @param PlotData: Overplot raw data points over contour?
    @param levels: Define levels for contour plot (if None, pylab will create automatic levels)
    @warning: This is not tested for nasty inputs!
    @warning: No Exceptions are raised at any point
    @todo: Create possibility for log-file output.
    """
    def __init__(self,input,InData=True,CFill=True,PlotData=False,levels=None):
        if InData == True:
            self.kde = scipy.stats.gaussian_kde([input[0],input[1]])
            self.data = input
        elif InData == False:
            self.kde = input
        self.CFill = CFill
        self.PlotData = PlotData
        self.levels = levels
    def contour(self,x_vec,y_vec,return_data=False):
        """
        Plotting a contour of the KDE
        See Class main for all input parameters
        @type x_vec: array
        @type y_vec: array
        @param x_vec: X Vector along which KDE is evaluated
        @param y_vec: Y Vector along which KDE is evaluated
        @note: inherits parameters from main class 
        @note: I am not quite sure what contour does on funny vectors (unqeually spaced.....)
        @note: self.test is for veryfing that the x,y order is kept intact properly by contour (I believe its now in order)
        """
        self.x_vec = x_vec
        self.y_vec = y_vec
        self.z = []
        self.test = []
        for x in x_vec:
            for y in y_vec:
              tmp = self.kde.evaluate([x,y])[0]
              self.z.append(tmp)
              self.test.append([x,y,tmp])
        self.z = numpy.array(self.z)
        self.test = numpy.array(self.test)
        self.z_matrix = numpy.reshape(self.z,[len(x_vec),len(y_vec)])
        if return_data:
            return x_vec, y_vec, self.z_matrix.transpose(), self.levels, self.data[0], self.data[1]
        else:
            self.figure = pylab.figure()
            self.axes = self.figure.add_subplot(111)
            if self.CFill == False:
                self.axes.contour(x_vec,y_vec,self.z_matrix.transpose(),levels=self.levels)
            if self.CFill == True:
                self.axes.contourf(x_vec,y_vec,self.z_matrix.transpose(),levels=self.levels)
            if self.PlotData:
                self.axes.plot(self.data[0],self.data[1],ls='None',marker='.',c='k')
            self.figure.show()
    def OpenInteractive(self,sampling=100):
        """
        Opens an Interactive Window for Evaluating the KDE
        @type sampling: int
        @param sampling: sampling for vector extraction (OBSOLETE????)
        @warning: Open Only after a Contour has been created!
        """
        print "--------------This is an interactive KDE Analyzer--------------"
        print "You can extract a vector or integrate over a rectangular box"
        print "Choose a vector or box  by clicking on the KDE."
        print "Press 'h' to see all options."
        self.cid_click = self.figure.canvas.mpl_connect('button_press_event', self._onclick)
        self.cid_key = self.figure.canvas.mpl_connect('key_press_event', self._onkey)
        self.coos = []
        self.sampling = sampling
    def _onclick(self,event):
        """
        Helper Function for Pylab Interactive Session
        Defines Mouse Interaction
        @type event: some pylab instance
        @param event: this is created by pylab
        """
        #print 'button=%d, x=%d, y=%d, xdata=%f, ydata=%f'%(
        #event.button, event.x, event.y, event.xdata, event.ydata)
        tmp = [event.button, event.x, event.y, event.xdata, event.ydata]
        print "You clicked at x,y coordinates: " + str(tmp[3]) + ','  + str(tmp[4])
        self.coos.append(tmp)
        self.axes.plot([tmp[3]],[tmp[4]],ls='None',marker='o',ms=5,c='r') 
        self.figure.show()
    def _onkey(self,event):
        """
        Helper Function for Pylab Interactive Session
        Defines Keyboard Interaction
        @type event: some pylab instance
        @param event: this is created by pylab
        """
        print 'You just pressed: ', event.key
        if event.key in ('q','Q'):
            self._disconnect()
            pylab.close(1)
            print "ByeBye"
        elif event.key in ('e','E'):
            self._Extract()
        elif event.key in ('n','N'):
            print "You pressed 'n/N'"
            print "Define a new vector."
            try:
                pylab.close(2)
            except:
                pass
            self.coos = []
        elif event.key in ('c','C'):
            self.axes.clear()
            if self.CFill == False:
                self.axes.contour(self.x_vec,self.y_vec,self.z_matrix.transpose(),levels=self.levels)
            elif self.CFill == True:
                self.axes.contourf(self.x_vec,self.y_vec,self.z_matrix.transpose(),levels=self.levels)
            if self.PlotData:
                self.axes.plot(self.data[0],self.data[1],ls='None',marker='.',c='k')
            self.figure.show()
        elif event.key in ('i','I'):
            self._Integrate()
        elif event.key in ('h','H'):
            print "-------------------------------------------------"
            print "'e': extract a vector"
            print "'i': integrate over a rectangular box"
            print "'n': clear list of clicks and restart extracting"
            print "'c': clear the plot"
            print "'h': print help"
            print "'z': zoom"
            print "'u': unzoom"
            print "'q': quit"
            print "All other keys are inactive."
            print "Click to set pointers."
            print "-------------------------------------------------"
        elif event.key in ('z','Z'):
            self._Zoom()
        elif event.key in ('u','U'):
            pylab.xlim(min(self.x_vec,),max(self.x_vec))
            pylab.ylim(min(self.y_vec,),max(self.y_vec))
            print "Unzoomed."
        else:
            print "The key you pressed is inactive."
    def _disconnect(self):
        """
        Helper Function for Pylab Interactive Session
        Disconnects the Interactive Session
        """
        self.figure.canvas.mpl_disconnect(self.cid_click)
        self.figure.canvas.mpl_disconnect(self.cid_key)
    def _Extract(self):
        """
        Extracts the KDE along a vector
        Requires Interactive Session to be running
        @warning: Not directly accesible, only talks to the Interactive Session!
        """
        if len(self.coos) < 2:
            print "You did not click often enough, try again!"
            print "Flushing coordinates"
            self.coos = []
            return
        elif len(self.coos) == 2:
            self.x_start = self.coos[0][3]
            self.y_start = self.coos[0][4]
            self.x_end = self.coos[1][3]
            self.y_end = self.coos[1][4]
            self.axes.plot([self.x_start,self.x_end],[self.y_start,self.y_end],ls='-',lw=3,c='g')
            self.figure.show()
            print "Sampling along the following vector:"
            print "Starting Point:" + str(self.x_start) +',' + str(self.y_start)
            print "End Point:" + str(self.x_end) +',' + str(self.y_end)
            print "Sampling is " + str(self.sampling)
            self.x_ext = numpy.linspace(self.x_start,self.x_end,self.sampling)
            self.y_ext = numpy.linspace(self.y_start,self.y_end,self.sampling)
            self.sample_points = numpy.array([self.x_ext,self.y_ext])
            self.sampled_along_vector = self.kde.evaluate(self.sample_points) 
            self.fig_new = pylab.figure(2)
            self.ax_new = host_subplot(111, axes_class=AA.Axes)
            self.ax_new.plot(numpy.arange(self.sampling),self.sampled_along_vector,ls='-',marker='None',c='r',lw=4)
            self.ax_new2 = self.ax_new.twin()
            self.ax_new2.set_xticks(numpy.arange(self.sampling)[::10][1:])
            self.ax_new2.set_xticklabels(numpy.array(self.y_ext[::10][1:],dtype='S5'))
            self.ax_new.set_xticks(numpy.arange(self.sampling)[::10][1:])
            self.ax_new.set_xticklabels(numpy.array(self.x_ext[::10][1:],dtype='S5'))
            self.ax_new.axis["bottom"].set_label("X")
            self.ax_new2.axis["top"].set_label("Y")
            
            print "There you go!"
            print "Press 'n' to close this plot and see another vector."
            print "Press 'q' to stop extracting vectors!"
            return
        else:
            print "You seem to have clicked too often."
            print "Flushing coordinates...."
            self.coos = []
    def _Integrate(self):
        """
        Integrates the KDE over a box.
        Requires Interactive Session to be running
        @warning: Not directly accesible, only talks to the Interactive Session!
        """
        if len(self.coos) < 2:
            print "You did not click often enough, try again!"
            print "Flushing coordinates"
            self.coos = []
            return
        elif len(self.coos) == 2:
            self.x_start = self.coos[0][3]
            self.y_start = self.coos[0][4]
            self.x_end = self.coos[1][3]
            self.y_end = self.coos[1][4]
            self.axes.plot([self.x_start,self.x_end],[self.y_start,self.y_start],ls=':',lw=3,c='k')
            self.axes.plot([self.x_start,self.x_end],[self.y_end,self.y_end],ls=':',lw=3,c='k')
            self.axes.plot([self.x_start,self.x_start],[self.y_start,self.y_end],ls=':',lw=3,c='k')
            self.axes.plot([self.x_end,self.x_end],[self.y_start,self.y_end],ls=':',lw=3,c='k')
            self.figure.show()
            result = abs(self.kde.integrate_box([self.x_start,self.y_start],[self.x_end,self.y_end]))
            print "The integral over the following box:"
            print "startx,starty/endx,endy = " + str(self.coos[0][3:]) + str(',') + str(self.coos[1][3:])
            print "Is: "  + str(result)
            print "Flushing coordinates..."
            self.coos = []
        else:
            print "You seem to have clicked too often."
            print "Flushing coordinates...."
            self.coos = []
    def _Zoom(self):
        """
        Zooms the Interactive Plot
        Requires Interactive Session to be running
        @warning: Not directly accesible, only talks to the Interactive Session!
        @bug: zooming can flip the axes if that's how the user clicked! This is confusing
        """
        if len(self.coos) < 2:
            print "You did not click often enough, try again!"
            print "Flushing coordinates"
            self.coos = []
            return
        elif len(self.coos) == 2:
            self.x_start = self.coos[0][3]
            self.y_start = self.coos[0][4]
            self.x_end = self.coos[1][3]
            self.y_end = self.coos[1][4]
            pylab.xlim(self.x_start,self.x_end)
            pylab.ylim(self.y_start,self.y_end)
            print "Zoomed, press 'u' to unzoom."
            print "Flushing coordinates..."
            self.coos = []
        else:
            print "You seem to have clicked too often."
            print "Flushing coordinates...."
            self.coos = []
    def RePlot(self):
        """
        Replots the Contour
        Use after changing parameters
        @bug: Replot should not re-evaluate the KDE is x_vec and y_vec have not been updated!
        """
        pylab.close(1)
        pylab.close(2)
        self.contour(x_vec=self.x_vec,y_vec=self.y_vec)
    def Update(self,x_vec=False,y_vec=False,CFill=-999,PlotData=-999,levels =False):
        """
        Update Class Parameters
        Use Replot to Create an updated plot, then open an interactive Session.
        All parameters as in Main Class
        """
        updated = False
        if x_vec:
            self.x_vec = x_vec
            print "Updated x_vec to: " + str(self.x_vec)
            updated = True
        if y_vec:
            self.y_vec = y_vec
            print "Updated y_vec to: " + str(self.y_vec)
            updated = True
        if CFill != -999:
            self.CFill = CFill
            print "Updated CFill to: " + str(self.CFill)
            updated = True
        if PlotData != -999:
            self.PlotData = PlotData
            print "Updated PlotData to: " + str(self.PlotData)
            updated = True
        if levels:
            self.levels = levels
            print "Updated levels to: " + str(self.levels)
            updated = True
        if updated == False:
            print "Nothing updated."
    def Info(self):
        """
        Prints out all current parameters
        """
        print "-------Current AnaKDE Parameters-------"
        print "-------InData (Data Input?)------------"
        print str(self.Indata)
        print "---CFill (Plotting Filled contours?)---"
        print str(self.CFill)
        print "-----PLotData (Plotting data?)---------"
        print str(self.PlotData)
        print "------x_vec (X Samplin Vector)---------"
        print str(self.x_vec)
        print "------y_vec (X Samplin Vector)---------"
        print str(self.y_vec)
        print "---levels (Levels for Contour Plot)----"
        if self.levels == None:
            print "Automatic"
        else:
            print str(self.levels)
        
        
        
        
