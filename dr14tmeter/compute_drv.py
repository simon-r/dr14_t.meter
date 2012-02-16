# dr14_t.meter: compute the DR14 value of the given audiofiles
#Copyright (C) 2011  Simone Riva
#
#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.


from numpy  import *
from dr14tmeter.audio_math import *
import math
import numpy

def compute_DRV( Y , Fs , duration = None , Dr_lr = None ) :
    
    s = Y.shape
    ch = s[1]  
    
    block_time = 1
    block_samples = block_time * ( Fs )
    
    threshold = 0.15    
    seg_cnt = floor( sizeY(1) / block_samples )
    
    if seg_cnt < 3 :
        return ( 0 , -100 , -100 )

    curr_sam = 0   
    
    rms = zeros((seg_cnt,ch))
    peaks = zeros((seg_cnt,ch))    
    
    for i in range( seg_cnt - 1) :
        r = arange( curr_sam , curr_sam + block_sam )
        
    
    return 1
