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
    plot_track_classic( on_select.plot_str.Y , on_select.plot_str.Fs , Plot=False , plot_str=on_select.plot_str , start_time=vmin , end_time=vmax )
    on_select.plot_str.plot()
 
   
def mouse_pressed( event ) :
    
    dr14_log_debug( "mouse_pressed: " )
    
    if event.button == 3 :
        dr14_log_debug( "mouse_pressed: button 3" )
        m = mouse_pressed.plot_str.start_time + ( mouse_pressed.plot_str.end_time - mouse_pressed.plot_str.start_time ) / 2.0
        new_tot_time = 2.0 * ( mouse_pressed.plot_str.end_time - mouse_pressed.plot_str.start_time )
        
        start_time = m - new_tot_time/2.0
        end_time = m + new_tot_time/2.0
        
        dr14_log_debug( "mouse_pressed: start - end:  %f %f " % ( start_time , end_time ) )
        
        plot_track_classic( mouse_pressed.plot_str.Y , mouse_pressed.plot_str.Fs , Plot=False ,
                           plot_str=mouse_pressed.plot_str , start_time=start_time , end_time=end_time )
        
        mouse_pressed.plot_str.plot()
        

class PltTrackStruct:
    def __init__( self , plot_mode='fill' , t = [] , Y = [] , Fs=44100 , sz=0 , ch=0 ):
        self.ch = ch
        self.t = t
        self.start_time = 0 
        self.end_time = 0
        
        if plot_mode == 'fill' :
            self.mp = zeros( ( sz , ch ) )
            self.mn = zeros( ( sz , ch ) )
        else :
            self.mp = []
            self.mn = []
            
        self.Y = Y
        self.Fs = Fs
        self.plot_mode = plot_mode # or "curve"
        self.ax = None
        self.rebuild = False
        self.first_sample = 0
        self.sz_section = 0
        self.lines = []


    def plot( self ):
        
        new_flag = False
        
        if self.ax == None :
            self.ax = [i for i in range(self.ch)]
            self.lines = [i for i in range(self.ch)]
            self.span = []
            new_flag = True
            
            
        for j in range( self.ch ):
            
            #if new_flag :
            self.ax[j] = pyplot.subplot( 210+j+1 )
            
            if type( self.lines[j] ) is matplotlib.collections.PolyCollection :
                self.lines[j].remove()
            else:
                while ( not new_flag ) and len( self.lines[j] ) > 0:
                    l = self.lines[j].pop(0)
                    l.remove()
            
            if self.plot_mode == 'fill' :
                self.lines[j] = self.ax[j].fill_between( self.t ,  self.mp[:,j] ,  self.mn[:,j]  ) 
            else:
                self.lines[j] = self.ax[j].plot( self.t , self.Y[ self.first_sample:self.first_sample+self.sz_section , j ] , 'b' ) 
            
            pyplot.axis( [ self.start_time , self.end_time , -1.0 , 1.0 ] )
            
            self.ax[j].xaxis.set_major_formatter( MyTimeFormatter() )
            
            self.ax[j].grid(1)
            
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
            
        pyplot.show()
        
 
    

def plot_track_classic( Y , Fs , Plot=True , plot_str=None , utime=0.02 , time_lim=4 , start_time=0.0 , end_time = -1.0 ):
    
    time_a = time.time()
        
    s = Y.shape
    
    if len( Y.shape ) > 1 :
        ch = s[1]
    else :
        ch = 1
    
    if plot_str == None :    
        plot_str = PltTrackStruct( ch=ch )
        plot_str.Y = Y
        plot_str.Fs = Fs
        
    sz_section = s[0]
    first_sample = 0
    
    if end_time > s[0] * 1/Fs :
        end_time = s[0] * 1/Fs
        
    if start_time < 0 :
        start_time = 0
    
    if start_time >= 0 and end_time > start_time :
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
    
    if sz_section > time_lim*Fs:
        plot_str.plot_mode = "fill"
        plot_str.mp = zeros( ( sz , ch ) )
        plot_str.mn = zeros( ( sz , ch ) )
        plot_str.t = start_time + np.arange( 0 , sz ) * block_len
        for i in range( sz ):
            plot_str.mp[i,:] = np.max( Y[curr_sample:curr_sample+samples_block,:] , 0 )
            plot_str.mn[i,:] = np.min( Y[curr_sample:curr_sample+samples_block,:] , 0 )
            curr_sample = curr_sample + samples_block
    else:
        plot_str.plot_mode = "curve"
        plot_str.t = start_time + np.arange( sz_section ) * 1/Fs
        plot_str.first_sample = first_sample
        plot_str.sz_section = sz_section

    if Plot :
        plot_str.plot()
        
    return plot_str
    
    
    
    
    