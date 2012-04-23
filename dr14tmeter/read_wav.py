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

import scipy.io.wavfile
import sys
import wave
import numpy

class AudioArray(object):
    
    def __init__(self,*args):
        self.Y = numpy.array([])
        self.sampling_rate = 0 
        self.channels = 0 



#def read_wav_new( file_name , aar ):
#    
#    convert_8_bit = float(2**15)
#    convert_16_bit = float(2**15)
#    convert_32_bit = float(2**31)
#    
#    try:
#        wave_read = wave.open( file_name , 'r' )
#        aar.channels = wave_read.getnchannels()
#        aar.sampling_rate = wave_read.getframerate()
#        sample_width = wave_read.getsampwidth()
#        
#        #print( str(channels) + " " + str(sample_width ) + " " + str( sampling_rate ) + " " + str( wave_read.getnframes() ) )
#        
#        X = wave_read.readframes( wave_read.getnframes() )
#        
#        sample_type = "int%d" % (sample_width*8)
#        aar.Y = numpy.fromstring(X, dtype=sample_type)
#        
#        wave_read.close()
#
#        if sample_type == 'int16':
#            aar.Y = aar.Y / (convert_16_bit + 1.0)
#        elif sample_type == 'int32':
#            aar.Y = aar.Y / (convert_32_bit + 1.0)
#        else :
#            aar.Y = aar.Y / (convert_8_bit + 1.0)
#            
#    except:
#        aar.__init__()
#        print ( "Unexpected error:", str( sys.exc_info() ) )
#        print (  "\n - ERROR ! " )
#        return False
# 
#    return True

    


def read_wav( file_name ):

    convert_8_bit = float(2**15)
    convert_16_bit = float(2**15)
    convert_32_bit = float(2**31)
    
    try:
        sample_rate, samples = scipy.io.wavfile.read(file_name)
        if samples.dtype == 'int16':
            samples = samples / (convert_16_bit + 1.0)
        elif samples.dtype == 'int32':
            samples = samples / (convert_32_bit + 1.0)
        else :
            samples = samples / (convert_8_bit + 1.0)
    except:
        #print ( "Unexpected error:", str( sys.exc_info() ) )
        print (  "\n - ERROR ! " )
        return ( [] , 0 , 0 )
        
        
    s = samples.shape
    
    if len(s) == 1:
        channels = 1 
    else:
        channels = s[1]
        
    return ( samples , sample_rate , channels )
    
