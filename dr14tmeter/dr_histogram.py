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
import matplotlib.pyplot as pyplot
import matplotlib.mlab as mlab


def compute_hist ( Y , Fs , duration=None , bins=None , block_duration = 0.2 , plot=True ):
    s = Y.shape
    
    if len( Y.shape ) > 1 :
        ch = s[1]
    else :
        ch = 1

    saples_per_block = int( Fs * block_duration )
    
    seg_cnt = int( math.floor( float(s[0]) / saples_per_block ) ) + 1 
    
    if seg_cnt < 3:
        return False
    
    curr_sam = 0
    rms = zeros((seg_cnt,ch))
    
    #peaks = zeros((seg_cnt,ch))
    
    for i in range(seg_cnt - 1):
        r = arange( curr_sam , curr_sam + saples_per_block )
        rms[i,:] = u_rms( Y[r,:] )
        curr_sam = curr_sam + saples_per_block
       
    i = seg_cnt - 1 ;
    r = arange( curr_sam,s[0] )
    
    if r.shape[0] > 0:
        rms[i,:] = dr_rms( Y[r,:] )
    
    rms[rms == 0.0] = audio_min16()
    rms = decibel_u( rms , sqrt(2.0) )
    
    if bins == None :
        bins = 100
    
    if plot == True :
        ( hst , bin_edges , patches ) = pyplot.hist( rms[:,1] , bins=bins)
                
        pyplot.xlabel('RMS dB')
        pyplot.ylabel('Frequancy')
        
        pyplot.title(r'$\mathrm{Histograo\ of\ DR}')
        
        #pyplot.grid(True)

        pyplot.show()
        
    else:
        ( hist , bin_edges ) = numpy.histogram( rms , bins=bins )
    return ( hist , bin_edges )
    
    