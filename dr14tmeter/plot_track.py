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

def f_utime( t ) :
    v = 0.25
    a = 1/400
    xl = 200
    if t > xl :
        return a*t + (v-a*xl)
    else:
        return v
    

def plot_track( Y , Fs , Plot=True , time_range=None , utime = 0 ):
    
    time_a = time.time()
        
    s = Y.shape
    
    if len( Y.shape ) > 1 :
        ch = s[1]
    else :
        ch = 1
    
    ttime = (s[0] * 1/Fs)
    if utime == 0 :
        d = ttime / f_utime(ttime) ;
        utime = ttime / d
        #print( utime )
    
    Fs = int(Fs * utime)
    
    sec = floor( s[0] / Fs ) + 1   
    sz = Fs * ( sec + 1 )
    tm = floor( np.arange(sz) / Fs )
     
    Yc = np.zeros( sz , dtype=np.float32 )
    
    for i in range(ch):
        
        ax = pyplot.subplot( 210+i+1 )
               
        Yc[:] = 0.0
        Yc[0:s[0]] = Y[:,1]
        
        (H, xedges, yedges) = np.histogram2d( tm , Yc , bins=( sec , 500 ))
        
        mh = np.max( H , 1 )
        H = (H.T * (1/mh))
                
        ax.xaxis.set_major_formatter( MyTimeFormatter( utime ) )
        pyplot.xticks(rotation=25)
        
        extent = [xedges[0], xedges[-1], yedges[-1], yedges[0]]
        pyplot.imshow(H, extent=extent, interpolation='nearest',aspect='auto' , cmap="hot" )

        
    pyplot.show()        
    
    
    time_b = time.time()
    dr14_log_info( "plot_track: Clock: %2.8f" % (time_b - time_a ) )
    
    