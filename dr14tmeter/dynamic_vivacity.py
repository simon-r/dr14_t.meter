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
from dr14tmeter.out_messages import *
from dr14tmeter.my_time_formatter import *

import math
import time

try:
    import matplotlib 
    import matplotlib.pyplot as pyplot
    import matplotlib.mlab as mlab
except:
    ____foo = None
    

def dynamic_vivacity( Y , Fs , Plot=True ):
    
    time_a = time.time()
        
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
        #r = numpy.arange( curr_sample , curr_sample + samples_per_block )
        rms = u_rms( Y[curr_sample : curr_sample + samples_per_block , : ] )
        mx = numpy.max( Y[ curr_sample : curr_sample + samples_per_block  ,:] , 0 )
        seg_dyn[i,:] = decibel_u( mx , rms )
        iz = ( rms < audio_min() )
        seg_dyn[i,iz] = 0.0
        curr_sample = curr_sample + samples_per_block
        
    i = seg_cnt - 1 ;
    r = numpy.arange( curr_sample , s[0] )
    
    if r.shape[0] > 0:
        rms = u_rms( Y[r,:] )
        mx = numpy.max( Y[r,:] )
        seg_dyn[i,:] = decibel_u( mx , rms )
        iz = ( rms < audio_min() )
        seg_dyn[i,iz] = 0.0
        
    
    t = numpy.arange( 0.0 , math.floor((1.0/Fs) * s[0]) + 1 , step=block_size  )
        
    max_db = numpy.max( seg_dyn )
    
    non_zeros_ = seg_dyn >= audio_min()
    
    non_zeros = numpy.ones( ( seg_dyn.shape[0] ) ) == 1
    
    for i in range( ch ):
        non_zeros = numpy.logical_and( non_zeros , non_zeros_[:,i] ) 
        
    mean = numpy.mean( seg_dyn[non_zeros,:] , 0 )
    std = numpy.std( seg_dyn[non_zeros,:] , 0 )
    
    tot_t = s[0]*1.0/Fs 
    
    time_b = time.time()
    dr14_log_info( "dynamic_vivacity: Clock: %2.8f" % (time_b - time_a ) )
    
    if Plot :
        for j in range( ch ):
            
            ax = pyplot.subplot( 210+j+1 )
            pyplot.plot( t.T , seg_dyn[:,j] , linewidth=2 , color = "b" )
            pyplot.grid(True)
            
            time_x = numpy.array( [ 0 , tot_t ] )
            mean_y = numpy.array( [ mean[j] , mean[j] ] )
            
            pyplot.plot( time_x , mean_y , linewidth=2 , color="g" )
            
            ax.xaxis.set_major_formatter( MyTimeFormatter() )
            pyplot.xticks(rotation=25)
            
            std_a_y = numpy.array( [ mean[j] , mean[j] ] + std[j] )
            std_b_y = numpy.array( [ mean[j] , mean[j] ] - std[j] )
            
            pyplot.plot( time_x , std_a_y , linewidth=2 , ls='--' , color='c' )
            pyplot.plot( time_x , std_b_y , linewidth=2 , ls='--' , color='c' )
            
            pyplot.axis( [ 0 , tot_t , 0 , max_db * 1.15 ] )
            
            text_rel_pos = 0.2
            pyplot.text( tot_t * 0.1 , max_db* text_rel_pos       , "mean:     %.3f dB"%mean[j] , fontsize=12)
            pyplot.text( tot_t * 0.1 , max_db*(text_rel_pos-0.07) , "std dev:  %.3f dB"%std[j] , fontsize=12)
                        
            pyplot.title( "Channel %d" % (j+1) )
            pyplot.xlabel('Time [min:sec]')
            pyplot.ylabel('Dynamic. [dB]')
            
        
        pyplot.show()


    
    return ( mean , std , seg_dyn )