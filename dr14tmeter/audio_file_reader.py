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

import time
import os
import sys
import tempfile
import subprocess
import re
import wave
import numpy
from dr14tmeter.out_messages import print_msg


class AudioFileReader:
    
    def __init__(self):
        if sys.platform.startswith('linux'):
            self.__cmd = "%s " % self.get_cmd()
        elif sys.platform.startswith('win'):
            self.__cmd = ".\\decoder\\%s " % self.get_cmd()

    def get_cmd(self):
        pass

    def get_cmd_options( self , file_name , tmp_file ):
        pass

    def to_wav( self , file_name ):
        
        full_command = self.__cmd
        
        (head, file) = os.path.split( file_name )
        tmp_dir = tempfile.gettempdir()
        tmp_file = os.path.join( tmp_dir , file ) + ".wav"
        
        file_name = re.sub( "(\"|`)" , r"\\\1" , file_name )
        tmp_file = re.sub( "(\"|`)" , r"_xyz_" , tmp_file )
        
        full_command = full_command + " " + self.get_cmd_options( file_name , tmp_file )
        
        r = subprocess.call( full_command , shell=True  , stderr=subprocess.PIPE , stdout=subprocess.PIPE )
        
        if os.path.exists( tmp_file ) :
            return tmp_file
        else :
            return "" 
  

    def read_audio_file_new( self , file_name , target ):
                
        full_command = self.__cmd
        
        (head, file) = os.path.split( file_name )
        tmp_dir = tempfile.gettempdir()
        tmp_file = os.path.join( tmp_dir , file ) + ".wav"
        
        file_name = re.sub( "(\"|`)" , r"\\\1" , file_name )
        tmp_file = re.sub( "(\"|`)" , r"_xyz_" , tmp_file )
    
        full_command = full_command + " " + self.get_cmd_options( file_name , tmp_file )
            
        #print_msg( full_command )
        
        r = subprocess.call( full_command , shell=True  , stderr=subprocess.PIPE , stdout=subprocess.PIPE )
        
        #read_wav.read_wav( tmp_file )
        
        ret_f = self.read_wav( tmp_file , target )
        
        if os.path.exists( tmp_file ) :
            os.remove( tmp_file )
        else:
            print_msg( file_name + ": unsupported encoder" )
                
        return ret_f 


    def read_wav( self , file_name , target ):
    
        convert_8_bit = float(2**15)
        convert_16_bit = float(2**15)
        convert_32_bit = float(2**31)
                
        try:
            wave_read = wave.open( file_name , 'r' )
            target.channels = wave_read.getnchannels()
            target.Fs = wave_read.getframerate()
            target.sample_width = wave_read.getsampwidth()
            
            nframes = wave_read.getnframes()
            #print_msg( file_name + "!!!!!!!!!!!!: " + str(target.channels) + " " + str(target.sample_width ) + " " + str( target.Fs ) + " " + str( nframes ) )
            
            X = wave_read.readframes( wave_read.getnframes() )
            
            # 24 bit support ??
            #if target.sample_width == 3:
            #    new_X = ""
            #    for i in range(0, len(X)/3):
            #        new_X += '\x00' + X[3*i:3*i+3]
            #    X = new_X
            #    sample_width = 4
            #
            sample_type = "int%d" % ( target.sample_width * 8 )
            
            target.Y = numpy.fromstring(X, dtype=sample_type).reshape( nframes , target.channels )
        
            wave_read.close()
    
            if sample_type == 'int16':
                target.Y = target.Y / (convert_16_bit + 1.0)
            elif sample_type == 'int32':
                target.Y = target.Y / (convert_32_bit + 1.0)
            else :
                target.Y = target.Y / (convert_8_bit + 1.0)
                
        except:
            self.__init__()
            print_msg ( "Unexpected error:", str( sys.exc_info() ) )
            print_msg (  "\n - ERROR ! " )
            return False
     
        return True




class Mp3FileReader( AudioFileReader ):
    def get_cmd(self):
        return "lame"
    
    def get_cmd_options(self , file_name , tmp_file ):
        return "--silent " + "--decode " + "\"" + file_name + "\"" + " \"%s\" " % tmp_file


class FlacFileReader( AudioFileReader ):
    def get_cmd(self):
        return "flac"
    
    def get_cmd_options(self , file_name , tmp_file ):
        return "-s " + "-d " + "\"" + file_name + "\"" + " -o \"%s\" " % tmp_file


class Mp4FileReader( AudioFileReader ):
    def get_cmd(self):
        return "ffmpeg"
    
    def get_cmd_options(self , file_name , tmp_file ):
        return  " -i \"" + file_name + "\"" + " -y \"%s\" -loglevel quiet -y " % tmp_file


class OggFileReader( AudioFileReader ):
    def get_cmd(self):
        return "oggdec"
    
    def get_cmd_options(self , file_name , tmp_file ):
        return  "--quiet " + "\"" + file_name + "\"" + " --output \"%s\"  " % tmp_file

class ApeFileReader( AudioFileReader ):
    def get_cmd(self):
        return "ffmpeg"
    
    def get_cmd_options(self , file_name , tmp_file ):
        return  " -i \"" + file_name + "\"" + " -y \"%s\" -loglevel quiet -y " % tmp_file


class WmaFileReader( AudioFileReader ):
    def get_cmd(self):
        return "ffmpeg"
    
    def get_cmd_options(self , file_name , tmp_file ):
        return  " -i \"" + file_name + "\"" + " -y \"%s\" -loglevel quiet " % tmp_file


class WavFileReader( AudioFileReader ):
    def read_audio_file_new( self , file_name , target ):
        return self.read_wav( file_name , target )
    
    def get_cmd(self):
        return ""

    def get_cmd_options( self , file_name , tmp_file ):
        return ""

