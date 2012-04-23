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
import dr14tmeter.read_wav as read_wav
import os
from dr14tmeter.audio_decoder import AudioDecoder


class AudioTrack:

    def __init__(self):
        self.Y = numpy.array([])
        self.Fs = 0
        self.channels = 0
        self.sample_width = 0 

    def time(self):
        return 1/self.Fs * self.Y.shape[0]

    def open( self , file_name ):

        self.Y = numpy.array([])
        self.Fs = 0
        self.channels = 0

        if not ( os.path.exists( file_name ) ) :
            return False

        ( f , ext ) = os.path.splitext( file_name )

        de = AudioDecoder()

        if ext == '.wav':
            ( self.Y , self.Fs , self.channels ) = read_wav.read_wav( file_name )
        elif ext in de.formats:
            ( self.Y , self.Fs , self.channels ) = de.read_track( file_name )

        #print( file_name )

        if self.channels == 0:
            return False
        else:
            return True
        
        
    def read_wav( self , file_name ):
    
        convert_8_bit = float(2**15)
        convert_16_bit = float(2**15)
        convert_32_bit = float(2**31)
        
        try:
            wave_read = wave.open( file_name , 'r' )
            self.channels = wave_read.getnchannels()
            self.Fs = wave_read.getframerate()
            self.sample_width = wave_read.getsampwidth()
            
            #print( str(channels) + " " + str(sample_width ) + " " + str( sampling_rate ) + " " + str( wave_read.getnframes() ) )
            
            X = wave_read.readframes( wave_read.getnframes() )
            
            sample_type = "int%d" % (sample_width*8)
            self.Y = numpy.fromstring(X, dtype=sample_type)
            
            wave_read.close()
    
            if sample_type == 'int16':
                self.Y = self.Y / (convert_16_bit + 1.0)
            elif sample_type == 'int32':
                self.Y = self.Y / (convert_32_bit + 1.0)
            else :
                self.Y = self.Y / (convert_8_bit + 1.0)
                
        except:
            self.__init__()
            print ( "Unexpected error:", str( sys.exc_info() ) )
            print (  "\n - ERROR ! " )
            return False
     
        return True
