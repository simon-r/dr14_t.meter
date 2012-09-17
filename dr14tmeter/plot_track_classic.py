# dr14_t.meter: compute the DR14 value of the given audiofiles
# Copyright (C) 2011  Simone Riva
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
except:
    ____foo = None

    

def plot_track_classic( Y , Fs , Plot=True , time_range=None , utime = 0.02 , title=None ):
    
    time_a = time.time()
        
    s = Y.shape
    
    if len( Y.shape ) > 1 :
        ch = s[1]
    else :
        ch = 1
        
    tot_t = s[0] * 1.0/Fs
    
    block_len = utime
    
    samples_block = block_len * Fs
    sz = int( s[0] / samples_block )
    
    mp = zeros( ( sz , ch ) )
    mn = zeros( ( sz , ch ) )
    
    curr_sample = 0 
    for i in range( sz ):
        mp[i,:] = np.max( Y[curr_sample:curr_sample+samples_block,:] , 0 )
        mn[i,:] = np.min( Y[curr_sample:curr_sample+samples_block,:] , 0 )
        curr_sample = curr_sample + samples_block
    
    t = np.arange( 0 , sz ) * block_len
    
    for j in range( ch ):
        ax = pyplot.subplot( 210+j+1 )
        
        ax.fill(t,  mp[:,j], 'b', t,  mn[:,j], 'b')
        
        pyplot.axis( [ 0 , tot_t , -1 , 1 ] )
        
        ax.xaxis.set_major_formatter( MyTimeFormatter() )
        #pyplot.xticks(rotation=10)
        
        pyplot.grid(1)
        
        pyplot.title( "Channel %d" % (j+1) )
        pyplot.xlabel('Time [min:sec]')
        pyplot.ylabel('Amplitude')
        
    pyplot.show()
        
        
    
    
    
    
    