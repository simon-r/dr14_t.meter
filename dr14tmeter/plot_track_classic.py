# dr14_t.meter: compute the DR14 value of the given audiofiles
# Copyright (C) 2012  Simone Riva
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import numpy as np
from dr14tmeter.audio_math import *
from dr14tmeter.out_messages import *
from dr14tmeter.my_time_formatter import *

import math
import time
import datetime

try:
    import matplotlib.pyplot as pyplot
    import matplotlib.mlab as mlab
    from matplotlib import dates
    from matplotlib.widgets import  *
    from pylab import *
except:
    ____foo = None

  
def on_select(vmin, vmax):
    dr14_log_debug( "on_select: %f , %f " % (vmin , vmax) )
    if vmin == vmax :
        return 
    plot_track_classic( plot_str=on_select.plot_str , start_time=vmin , end_time=vmax )
    on_select.plot_str.plot()
 

def wheel_moved( event ) :
    dr14_log_debug( "mouse_pressed: step: %d " % event.step )
    
    ( start_time , end_time ) = wheel_moved.plot_str.move( event.step )
    plot_track_classic( plot_str=wheel_moved.plot_str , start_time=start_time , end_time=end_time )
    wheel_moved.plot_str.plot()

   
def mouse_pressed( event ) :
    
    dr14_log_debug( "mouse_pressed: " )
    
    if event.button == 3 :
        dr14_log_debug( "mouse_pressed: button 3" )
        
        ( start_time , end_time ) = mouse_pressed.plot_str.zoom_out()              
        plot_track_classic( plot_str=mouse_pressed.plot_str , start_time=start_time , end_time=end_time )
        mouse_pressed.plot_str.plot()
        
        dr14_log_debug( "mouse_pressed: start - end:  %f %f " % ( start_time , end_time ) )
        

class PltTrackStruct:
    def __init__( self , plot_mode='fill' , Y = [] , Fs=44100 , sz=0 , ch=0 ):
        self.ch = ch
        self.tot_time = 0
        
        self.t = None
        self.tb = None
        self.start_time = 0 
        self.end_time = 0
        
        self.start_block = 0  
        self.end_block = 0 
        
        self.mp = None
        self.mn = None
            
        self.Y = Y
        self.Fs = Fs
        self.plot_mode = plot_mode # "fill" or "curve"
        self.ax = None
        self.rebuild = False
        self.first_sample = 0
        self.sz_section = 0
        self.lines = []
        self.fig = None


    def start( self ) :
        self.plot()
        pyplot.show()        

    def zoom_out( self ) :
        start_time = self.start_time
        end_time   = self.end_time
        
        m = start_time + ( end_time - start_time ) / 2.0
        new_tot_time = 2.0 * ( end_time - start_time )
        
        start_time = m - new_tot_time/2.0
        end_time = m + new_tot_time/2.0
        
        return ( start_time , end_time )
    
    
    def move( self , sign ):
        
        factor = 0.05
        
        delta = self.end_time - self.start_time
        
        start_time = self.start_time + sign * delta * factor
        end_time   = self.end_time + sign * delta * factor
        
        if start_time < 0 or end_time > self.tot_time:
            start_time = self.start_time 
            end_time   = self.end_time
        
        return ( start_time , end_time )
    

    def plot( self ):
        
        new_flag = False
        
        if self.fig == None :
            self.fig = pyplot.figure()
            self.ax = [i for i in range(self.ch)]
            self.lines = [i for i in range(self.ch)]
            self.span = []
            new_flag = True
            
            
        for j in range( self.ch ):
            
            if new_flag :
                self.ax[j] = self.fig.add_subplot( 210+j+1 )
            
            if type( self.lines[j] ) is matplotlib.collections.PolyCollection :
                self.lines[j].remove()
            else:
                while ( not new_flag ) and len( self.lines[j] ) > 0:
                    l = self.lines[j].pop(0)
                    l.remove()
            
            if self.plot_mode == 'fill' :
                self.lines[j] = self.ax[j].fill_between( self.tb[ self.start_block:self.end_block ] ,
                                                         self.mp[ self.start_block:self.end_block , j ] ,
                                                         self.mn[ self.start_block:self.end_block , j ]  ) 
            else:
                self.lines[j] = self.ax[j].plot( self.t , self.Y[ self.first_sample : self.first_sample+self.sz_section , j ] , 'b' ) 
            
            self.ax[j].axis( [ self.start_time , self.end_time , -1.0 , 1.0 ] )
            
            delta_time = self.end_time - self.start_time
            
            if delta_time < 1.5 :
                milli_sec=True 
            else :
                milli_sec=False
            
            self.ax[j].xaxis.set_major_formatter( MyTimeFormatter( milli_sec=milli_sec ) )
            
            self.ax[j].grid(True)
            
            pyplot.title( "Channel %d" % (j+1) )
            pyplot.xlabel('Time [min:sec]')
            pyplot.ylabel('Amplitude')
        
            if new_flag :
                onsel = on_select
                onsel.plot_str = self
                self.span.append( SpanSelector( self.ax[j], onsel, 'horizontal' ) )
                
                m_p = mouse_pressed
                m_p.plot_str = self
                connect('button_press_event', m_p)
                
                w_m = wheel_moved
                w_m.plot_str = self
                connect('scroll_event', w_m)
            
        self.fig.canvas.draw()
        
 
    

def plot_track_classic( Y=None , Fs=None , plot_str=None , utime=0.02 , time_lim=5 , start_time=0.0 , end_time = -1.0 ):
        
    if Y == None and Fs == None and plot_str == None :
        raise
    
    if plot_str == None and Y != None and Fs != None :        
        s = Y.shape
        
        if len( Y.shape ) > 1 :
            ch = s[1]
        else :
            ch = 1           
        
        plot_str = PltTrackStruct( ch=ch )
        plot_str.Y = Y
        plot_str.Fs = Fs
        plot_str.tot_time = s[0] * 1.0/Fs
        
    elif plot_str != None :
        Fs = plot_str.Fs
        Y = plot_str.Y
        
        s = Y.shape
        if len( Y.shape ) > 1 :
            ch = s[1]
        else :
            ch = 1
    else:
        raise
     
    
    sz_section = s[0]
    first_sample = 0
    
    if end_time > s[0] * 1.0/Fs :
        end_time = s[0] * 1.0/Fs
        
    if start_time < 0 :
        start_time = 0.0
    
    if start_time >= 0.0 and end_time > start_time :
        sz_section = int( ( end_time - start_time ) * Fs )
        first_sample = int( start_time * Fs )
        plot_str.start_time = start_time
        plot_str.end_time = end_time
    else :
        plot_str.start_time = 0.0
        plot_str.end_time = sz_section * 1.0/Fs
            
    
    block_len = utime
    
    samples_block = block_len * Fs
    sz = int( sz_section / samples_block )
    
    curr_sample = first_sample
    
    if plot_str.mp != None and plot_str.mn != None and sz_section >= time_lim*Fs :
        plot_str.plot_mode = "fill"
        plot_str.start_block = int( plot_str.start_time / block_len )
        plot_str.end_block   = int( plot_str.end_time / block_len )
        
        return plot_str
        
    if sz_section > time_lim*Fs:
        plot_str.plot_mode = "fill"
        plot_str.mp = zeros( ( sz , ch ) )
        plot_str.mn = zeros( ( sz , ch ) )
        plot_str.tb = start_time + np.arange( 0 , sz ) * block_len
        
        for i in range( sz ):
            plot_str.mp[i,:] = np.max( Y[curr_sample:curr_sample+samples_block,:] , 0 )
            plot_str.mn[i,:] = np.min( Y[curr_sample:curr_sample+samples_block,:] , 0 )
            curr_sample = curr_sample + samples_block
        
        plot_str.start_block = 0
        plot_str.end_block = sz
        
    else:
        plot_str.plot_mode = "curve"
        plot_str.t = start_time + np.arange( 0 , sz_section ) * 1.0/Fs
        plot_str.first_sample = first_sample
        plot_str.sz_section = sz_section
        
    return plot_str
    
    
    
    
    