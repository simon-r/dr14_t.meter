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
    from scipy.interpolate import interp1d
except:
    ____foo = None


def dyn_compressor( Y , Fs , maxDB=-3.0 , linear_limit=0.3 ):
    
    x = numpy.linspace( -1 , 1 , 21 )
    y = c_fun( x , maxDB , linear_limit )
    
    int_f = interp1d( x , y , kind='cubic' )
       
    cY = int_f( Y )
    
    cY = normalize( cY )
        
    return cY


def c_fun( x , maxDB=-3.0 , linear_limit=0.3 ):
    
    z = linear_limit
    
    y = numpy.zeros( x.shape )
    
    r = numpy.abs(x)<=(z+z*10e-6)
    y[r] = 0.0
    
    r2 = numpy.abs(x)>z
    
    a = -maxDB / (z-1.0)
    b = -a * z
    
    y[r2] =  (a * numpy.abs(x[r2]) + b )
    
    return x * 10.0**( y / 20.0 )