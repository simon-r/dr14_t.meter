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

import dr14tmeter.read_wav as read_wav
import os
import sys
import tempfile
import subprocess

class AudioDecoder:

    def __init__(self):
        self.formats = [ '.flac' , '.mp3' , '.ogg' , '.mp4' , '.m4a' , '.wav' , '.ape' , '.wma' ]

    def read_track( self , file_name ):

        ( f , ext ) = os.path.splitext( file_name )

        if ext not in self.formats :
            return ( [] , 0 , 0 )

        af = AudioFileReader()
    
        if ext == '.mp3':
            af = Mp3FileReader()
        elif ext == '.flac':
            af = FlacFileReader()
        elif ext == '.ogg':
            af = OggFileReader()
        elif ext in ['.mp4' , '.m4a' ]:
            af = Mp4FileReader()
        elif ext == '.wav':
            af = WavFileReader()
        elif ext == '.ape':
            af = ApeFileReader()
        elif ext == '.wma':
            af = WmaFileReader()
        else:
            return ( [] , 0 , 0 )

        ( Y , Fs , channels ) = af.read_audio_file( file_name )
        return ( Y , Fs , channels )
        
 
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

    def read_audio_file( self , file_name ):
        
        full_command = self.__cmd
        
        (head, file) = os.path.split( file_name )
        tmp_dir = tempfile.gettempdir()
        tmp_file = os.path.join( tmp_dir , file ) + ".wav"
    
        full_command = full_command + " " + self.get_cmd_options( file_name , tmp_file )

        r = subprocess.check_output( full_command , shell=True  )
        
        ( Y , Fs , channels ) = read_wav.read_wav( tmp_file )
        #print (  "-fail- read mp3: " + tmp_file + str( ( Y , Fs , channels ) ) )
        os.remove( tmp_file )

        return ( Y , Fs , channels )



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
        return "faad"
    
    def get_cmd_options(self , file_name , tmp_file ):
        return  "-q " + "\"" + file_name + "\"" + " -o \"%s\"  " % tmp_file


class OggFileReader( AudioFileReader ):
    def get_cmd(self):
        return "oggdec"
    
    def get_cmd_options(self , file_name , tmp_file ):
        return  "--quiet " + "\"" + file_name + "\"" + " --output \"%s\"  " % tmp_file

class ApeFileReader( AudioFileReader ):
    def get_cmd(self):
        return "ffmpeg"
    
    def get_cmd_options(self , file_name , tmp_file ):
        return  " -i \"" + file_name + "\"" + " \"%s\" -y &> /dev/null " % tmp_file


class WmaFileReader( AudioFileReader ):
    def get_cmd(self):
        return "ffmpeg"
    
    def get_cmd_options(self , file_name , tmp_file ):
        return  " -i \"" + file_name + "\"" + " \"%s\" -y &> /dev/null " % tmp_file


class WavFileReader( AudioFileReader ):
    def read_audio_file( self , file_name ):
        return read_wav.read_wav( file_name )

