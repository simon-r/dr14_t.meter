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

import wave
    
def wav_write( filename , Fs , Y ):
    
    amplitude = 2.0**16 - 1.0
    
    wav_file = wave.open(filename, "w")
    
    s = Y.shape
    
    if len( Y.shape ) > 1 :
        nchannels = s[1]
    else :
        nchannels = 1
        
    sampwidth = 2
    framerate = int(Fs)
    
    nframes = s[0]
    comptype = "NONE"
    compname = "no comp"
    
    wav_file.setparams(( nchannels , sampwidth , framerate , nframes , comptype , compname ))
    
    Y_s = numpy.int16( (amplitude/2.0) * Y )
    Y_s = Y_s.tostring() ;
    
    wav_file.writeframes( Y_s )
        
    wav_file.close()
    