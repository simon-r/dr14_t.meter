import math
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
            return True
        elif ext in de.formats:
            ( self.Y , self.Fs , self.channels ) = de.read_track( file_name )
            return True
        
        return False
    
    