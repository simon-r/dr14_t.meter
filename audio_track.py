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

import numpy
import read_wav
import os
from audio_decoder import AudioDecoder


class AudioTrack:
    
    def __init__(self):
        self.Y = numpy.array([])
        self.Fs = 0
        self.channels = 0 
    
    def time(self):
        return 1/self.Fs * self.Y.shape[0]

    def open( self , file_name ):
        
        if not ( os.path.exists( file_name ) ) :
            return False
        
        ( f , ext ) = os.path.splitext( file_name )
        
        de = AudioDecoder()
        
        if ext == '.wav':
            ( self.Y , self.Fs , self.channels ) = read_wav.read_wav( file_name )
        elif ext in de.formats:
            ( self.Y , self.Fs , self.channels ) = de.read_track( file_name )
        
        if self.channels == 0:
            return False
        else:
            return True
        
    
    
