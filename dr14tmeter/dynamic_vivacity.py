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

import numpy
from dr14tmeter.audio_math import *
import math

try:
    import matplotlib.pyplot as pyplot
    import matplotlib.mlab as mlab
except:
    ____foo = None



def dynamic_vivacity( Y , Fs , Plot=True ):
        
    s = Y.shape
    
    if len( Y.shape ) > 1 :
        ch = s[1]
    else :
        ch = 1
        
    block_size = 1.0
    
    samples_per_block = int( Fs * block_size )
    
    seg_cnt = int( math.floor( s[0] / samples_per_block ) + 1 )
    
    seg_dyn = zeros(( seg_cnt , ch ))
    
    
    curr_sample = 0 
    for i in range( seg_cnt - 1 ):
        r = numpy.arange( curr_sample , curr_sample + samples_per_block )
        rms = u_rms( Y[r,:] )
        mx = numpy.max( Y[r,:] )
        seg_dyn[i,:] = decibel_u( mx , rms )
        curr_sample = curr_sample + samples_per_block
        
        
    i = seg_cnt - 1 ;
    r = numpy.arange( curr_sample , s[0] )
    
    if r.shape[0] > 0:
        rms = u_rms( Y[r,:] )
        mx = numpy.max( Y[r,:] )
        seg_dyn[i,:] = decibel_u( mx , rms )
    
    t = numpy.arange( 0.0 , math.floor((1.0/Fs) * s[0]) + 1 , step=block_size  )
        
    max_db = numpy.max( seg_dyn[:] )
    
    if Plot :
        for j in range( ch ):
            pyplot.subplot(210+j+1)
            pyplot.plot( t.T , seg_dyn[:,j] )
            pyplot.grid(True)
            pyplot.axis( [ 0 , s[0]*1.0/Fs , 0 , max_db * 1.15 ] )
            
            pyplot.title( "Channel %d" % (j+1) )
            pyplot.xlabel('Time [sec]')
            pyplot.ylabel('Dynamic. [dB]')
            
        
        pyplot.show()
    
    return seg_dyn