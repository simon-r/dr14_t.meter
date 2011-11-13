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

import read_wav
import os
import sys
import tempfile
import random

class AudioDecoder:
    
    def __init__(self):
        self.formats = [ '.flac' , '.mp3' , '.ogg' , '.mp4' , '.m4a' ]
    
    def read_track( self , file_name ):
        
        ( f , ext ) = os.path.splitext( file_name )
        
        if ext not in self.formats :
            return ( [] , 0 , 0 )
            
        if ext == '.mp3':
            ( Y , Fs , channels ) = read_mp3( file_name )
        elif ext == '.flac':
            ( Y , Fs , channels ) = read_flac( file_name )
        elif ext == '.ogg':
            ( Y , Fs , channels ) = read_ogg( file_name )
        elif ext in ['.mp4' , '.m4a' ]:
            ( Y , Fs , channels ) = read_mp4( file_name )
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
  
def read_ogg( file_name ):

    if sys.platform.startswith('linux'):
        ogg_cmd = "oggdec "
    elif sys.platform.startswith('win'):
        ogg_cmd = ".\decoder\oggdec "
    
    
    tmp_file = tempfile.mktemp() + ".wav"
    ogg_cmd = ogg_cmd + "--quiet " + "\"" + file_name + "\"" + " --output %s " % tmp_file
    
    print( file_name )
    
    r = os.popen( ogg_cmd ).read()
    ( Y , Fs , channels ) = read_wav.read_wav( tmp_file )
    os.remove( tmp_file )
    
    return ( Y , Fs , channels )
    
    
def read_mp4( file_name ):

    if sys.platform.startswith('linux'):
        mp4_cmd = "faad "
    elif sys.platform.startswith('win'):
        mp4_cmd = ".\decoder\faad "
    
    
    tmp_file = tempfile.mktemp() + ".wav"
    mp4_cmd = mp4_cmd + "-q " + "\"" + file_name + "\"" + " --o %s " % tmp_file
    
    print( file_name )
    
    r = os.popen( mp4_cmd ).read()
    ( Y , Fs , channels ) = read_wav.read_wav( tmp_file )
    os.remove( tmp_file )
    
    return ( Y , Fs , channels )