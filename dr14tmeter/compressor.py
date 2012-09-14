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
import time

from dr14tmeter.audio_math import *
from dr14tmeter.out_messages import *

try:
    from scipy.interpolate import interp1d
except:
    ____foo = None




class DynCompressor:
    
    def __init__(self):
        self.maxDB = -3.0
        self.linear_limit = 0.3

    def set_compression_modality( self , modality="medium" ):
        if modality == "very_soft" or modality == "v":
            self.maxDB = -2.0
            self.linear_limit = 0.5
        elif modality == "soft" or modality == "s" :
            self.maxDB = -3.0
            self.linear_limit = 0.3
        elif modality == "medium" or modality == "m" :
            self.maxDB = -5.0
            self.linear_limit = 0.3
        elif modality == "hard" or modality == "h" :
            self.maxDB = -7.0
            self.linear_limit = 0.3
        elif modality == "very_hard" or modality == "vh":
            self.maxDB = -9.0
            self.linear_limit = 0.2
        else:
            self.maxDB = -3.0
            self.linear_limit = 0.3
            
        print( "%f %f " % ( self.maxDB , self.linear_limit ) )


    def dyn_compressor( self , Y , Fs ):
        
        time_a = time.time()
        
        x = numpy.linspace( -1 , 1 , 21 )
        y = self.c_fun( x )
        
        int_f = interp1d( x , y , kind='cubic' )
           
        cY = int_f( Y )
        
        cY[:] = normalize( cY )
        
        time_b = time.time()
        dr14_log_info( "dyn_compressor: Clock: %2.8f" % (time_b - time_a ) )
            
        return cY
    
    
    def c_fun( self , x ):
        
        z = self.linear_limit
        
        y = numpy.zeros( x.shape )
        
        r = numpy.abs(x)<=(z+z*10e-6)
        y[r] = 0.0
        
        r2 = numpy.abs(x)>z
        
        a = -self.maxDB / (z-1.0)
        b = -a * z
        
        y[r2] =  (a * numpy.abs(x[r2]) + b )
        
        return x * 10.0**( y / 20.0 )
    
