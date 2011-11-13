import read_wav
import os


class AudioDecoder:
    
    def __init__(self):
        self.formats = [ '.flac' , '.mp3' ]
    
    def read_track( self , file_name ):
        
        ( f , ext ) = os.path.splitext( file_name )
        
        if ext not in self.formats :
            return ( [] , 0 , 0 )
            
        if ext == '.mp3':
            ( Y , Fs , channels ) = read_mp3( file_name )
        elif ext == '.flac':
            ( Y , Fs , channels ) = read_flac( file_name )