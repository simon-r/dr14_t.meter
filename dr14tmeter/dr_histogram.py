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

try:
    import matplotlib.pyplot as pyplot
    import matplotlib.mlab as mlab
except:
    ____foo = None


def compute_hist ( Y , Fs , duration=None , bins=100 , block_duration = 0.2 , plot=True , title=None ):
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
    
    for i in range( seg_cnt - 1 ):
        #r = arange( curr_sam , curr_sam + saples_per_block )
        rms[i,:] = u_rms( Y[curr_sam : curr_sam + saples_per_block , : ] )
        curr_sam = curr_sam + saples_per_block
       
    i = seg_cnt - 1 ;
    r = arange( curr_sam,s[0] )
    
    if r.shape[0] > 0:
        rms[i,:] = dr_rms( Y[r,:] ) 
    
    rms = numpy.sum( rms , 1 ) / float(ch)
    
    rms[rms==0.0] = audio_min16()
    rms = decibel_u( rms , 1.0 )
    
    rms_mean = numpy.mean( rms )
    rms_std = numpy.std( rms )
    rms_max = numpy.max( rms )
    
    abs_peak = decibel_u( numpy.max( numpy.abs( Y ) ) , 1.0 )
    
    if plot == True :
        ( hist , bin_edges , patches ) = pyplot.hist( rms , 100 , normed=True )
        
        mean_x = numpy.array([ rms_mean , rms_mean ])
        mean_y = numpy.array([ 0.0 , numpy.max(hist)*1.01 ])
        
        std_x = numpy.array([ rms_mean - rms_std , rms_mean + rms_std ])
        std_y = numpy.array([ numpy.max(hist)*0.7 , numpy.max(hist)*0.7 ])
        
        pyplot.plot( mean_x , mean_y , linewidth=2 , color='g')
        pyplot.plot( std_x , std_y , linewidth=2 , ls='--' , color='c')
        #print( hist )
        
        pyplot.axis([-92, 0, 0, numpy.max(hist)*1.05 ])
        
        text_rel_pos = 0.9
        pyplot.text( -85 , numpy.max(hist)*text_rel_pos        ,"mean:    %.3f dB"%rms_mean , fontsize=15,)
        pyplot.text( -85 , numpy.max(hist)*(text_rel_pos-0.05) ,"std dev:  %.3f dB"%rms_std , fontsize=15,)
        pyplot.text( -85 , numpy.max(hist)*(text_rel_pos-0.10) ,"peak:     %.3f dB"%abs_peak , fontsize=15,)
        pyplot.text( -85 , numpy.max(hist)*(text_rel_pos-0.15) ,"max rms:  %.3f dB"%rms_max , fontsize=15,)
        
        pyplot.xlabel('RMS dB')
        pyplot.ylabel('Probability')
        
        if title != None:
            hist_title = title
        else:
            hist_title = "Hystogram of dynamic"
        
        pyplot.title(r'%s'%hist_title)
        
        pyplot.plot( mean_x , mean_y )
        
        pyplot.grid(True)
        pyplot.show()
        
    else:
        ( hist , bin_edges ) = numpy.histogram( rms , bins=bins , normed=True )
             
    return ( hist , bin_edges )
    
    