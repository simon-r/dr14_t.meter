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

import math
import time

try:
    import matplotlib 
    import matplotlib.pyplot as pyplot
    import matplotlib.mlab as mlab
except:
    ____foo = None


try:
    class MyTimeFormatter( matplotlib.ticker.Formatter ):
        
        def __init__(self,utime=1.0 , milli_sec=False ):
            self.utime = utime
            self.milli_sec = milli_sec
        
        def __call__( self , x , pos=None ):
            minu = int( self.utime*x / 60 ) ;
            sec = int( self.utime*x - minu*60 )
            msec =  int ( 1000 * ( self.utime*x - int( self.utime*x ) ) )
            
            if self.milli_sec :
                return "%02d:%02d.%03d" % ( minu , sec , msec )
            else :
                return "%02d:%02d" % ( minu , sec )
except:
    class MyTimeFormatter:
        def __init__(self):
            raise
    
