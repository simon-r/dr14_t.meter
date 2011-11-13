import read_wav
import os
import sys
import tempfile
import random

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
        else:
            ( Y , Fs , channels ) = ( [] , 0 , 0 )
        
        
        return ( Y , Fs , channels ) 


def read_mp3( file_name ):

    if sys.platform.startswith('linux'):
        mp3_cmd = "lame "
    elif sys.platform.startswith('win'):
        mp3_cmd = ".\decoder\lame "
    
    
    tmp_file = tempfile.mktemp() + ".wav"
    mp3_cmd = mp3_cmd + "--silent " + "--decode " + "\"" + file_name + "\"" + " %s " % tmp_file
    
    print( file_name )
    
    r = os.popen( mp3_cmd ).read()
    ( Y , Fs , channels ) = read_wav.read_wav( tmp_file )
    os.remove( tmp_file )
    
    return ( Y , Fs , channels )
    

def read_flac( file_name ):

    if sys.platform.startswith('linux'):
        flac_cmd = "flac "
    elif sys.platform.startswith('win'):
        flac_cmd = ".\decoder\flac "
    
    
    tmp_file = tempfile.mktemp() + ".wav"
    flac_cmd = flac_cmd + "-s " + "-d " + "\"" + file_name + "\"" + " -o %s " % tmp_file
    
    print( file_name )
    
    r = os.popen( flac_cmd ).read()
    ( Y , Fs , channels ) = read_wav.read_wav( tmp_file )
    os.remove( tmp_file )
    
    return ( Y , Fs , channels )
  