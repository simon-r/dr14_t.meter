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


import subprocess
import sys
import os
import re
import hashlib

from dr14tmeter.audio_decoder import AudioDecoder
from dr14tmeter.dr14_global import get_ffmpeg_cmd

if sys.version_info[0] == 2:
    import ConfigParser
else:
    import configparser as ConfigParser
    
import StringIO


# Test example !!!!!
# a = subprocess.check_output( [ "ffprobe" , "-show_format" , "/media/esterno_xfs/data/Musica/Musica/aavv/01-blitzkrieg_bop_160_lame_abr.mp3" ] , stderr=subprocess.STDOUT , shell=False )


class UnreadableAudioFileException(Exception):
    pass

class RetirveMetadata:
    
    def __init__( self ):
        self._album = {}
        self._artist = {}
        self._tracks = {}
        self._disk_nr = []
        
        if get_ffmpeg_cmd() == "ffmpeg" :
            self.__ffprobe_cmd = "ffprobe"
        elif get_ffmpeg_cmd() == "avconv" :
            self.__ffprobe_cmd = "avprobe"        
    
    
    def scan_dir( self , dir_name , files_list=None ):
        
        self._album = {}
        self._tracks = {}
        self._artist = {}
        self._disk_nr = []
        
        if files_list == None:
            dir_name = os.path.abspath( dir_name )
            files_list = sorted( os.listdir( dir_name ) )
        
        ad = AudioDecoder()
        
        for file_name in files_list :
            
            ( fn , ext ) = os.path.splitext( file_name )
            full_file = os.path.join( dir_name , file_name )
            
            if ext in ad.formats :
                try :
                    self.scan_file( full_file )
                except UnreadableAudioFileException as euaf :
                    pass
                
        #print( self._tracks )
    
    
    def scan_file( self , file_name ):
                
        try:
            data_txt = subprocess.check_output( [ self.__ffprobe_cmd , "-show_format" , file_name ] , 
                                                stderr=subprocess.STDOUT , shell=False )
        except :
            data_txt = "ffprobe ERROR"
         
        if data_txt != "ffprobe ERROR" :
            try:
                data_txt = data_txt.decode(encoding='UTF-8')
            except:
                data_txt = data_txt.decode(encoding='ISO-8859-1')
        
        track = {} 
        ( foo , f_key ) = os.path.split( file_name )
        
        track['file_name'] = file_name
        
        re_flags = ( re.MULTILINE | re.IGNORECASE | re.UNICODE )
        
        m = re.search( r"\[FORMAT\](.*)\[/FORMAT\]" , data_txt , re_flags | re.DOTALL )
        if m != None:
            format_tags = m.group(1)
        else:
            self._tracks[f_key] = None
            raise UnreadableAudioFileException( "problematic file: file_name" )
        
        pattern = "[ \t\f\v]*([\S \t\f\v]+\S).*$"
                        
        m = re.search( r"^TAG:track=\s*(\d+).*$" , format_tags , re_flags )
        if m != None:
            track['track_nr'] = int( m.group(1) )
            
        m = re.search( r"^TAG:disc=\s*(\d+).*$" , format_tags , re_flags )
        if m != None:
            track['disk_nr'] = int( m.group(1) )
            self._disk_nr.append( int( int( m.group(1) ) ) )
                
        m = re.search( r"^TAG:GENRE=%s"%pattern , format_tags , re_flags )
        if m != None:
            track['genre'] = m.group(1)
                 
        m = re.search( r"^TAG:DATE=\s*(\d+).*$" , format_tags , re_flags )
        if m != None:
            track['date'] = m.group(1)
               
        m = re.search( r"^TAG:ARTIST=%s"%pattern , format_tags , re_flags )
        if m != None:
            self._artist.setdefault( m.group(1) , 0 )
            self._artist[m.group(1)] += 1
            track['artist'] = m.group(1)
                 
        m = re.search( r"^TAG:TITLE=%s"%pattern , format_tags , re_flags )
        if m != None:
            track['title'] = m.group(1)
            
        m = re.search( r"^TAG:ALBUM=%s"%pattern , format_tags , re_flags )
        if m != None:
            self._album.setdefault( m.group(1) , 0 )
            self._album[m.group(1)] += 1
            track['album'] = m.group(1)
              
        m = re.search( r"^size=\s*(\d+)\s*$" , format_tags , re_flags )
        if m != None:
            track['size'] = m.group(1)
               
        m = re.search( r"^bit_rate=\s*(\d+)\s*$" , format_tags , re_flags )
        if m != None:
            track['bitrate'] = m.group(1)
                
            
        
        ##########################################
        # string examples:   
        #Audio: flac, 44100 Hz, stereo, s16
        #Stream #0:0(und): Audio: alac (alac / 0x63616C61), 44100 Hz, 2 channels, s16, 634 kb/s
        #Stream #0:0(und): Audio: aac (LC) (mp4a / 0x6134706D), 44100 Hz, stereo, fltp, 255 kb/s (default
        #Stream #0:0: Audio: flac, 44100 Hz, stereo, s16        
        m = re.search( r"Stream.*Audio:(.*)$" , data_txt , re_flags )
        if m != None:
            fmt = m.group(1)
            #print(fmt)
            
        fmt = re.split( "," , fmt )
        
        #print( fmt )
        track['codec'] = re.search( "\s*(\w+)" , fmt[0] , re_flags ).group(1)
        track['sampling_rate'] = re.search( "\s*(\d+)" , fmt[1] , re_flags ).group(1)
        track['channel'] = re.search( "^\s*([\S][\s|\S]*[\S])\s*$" , fmt[2] , re_flags ).group(1)
        
        m = re.search( "(\d+)" , fmt[3] , re_flags )
        if m != None:
            track['bit'] = m.group(1) 
        else :
            track['bit'] = "16"
            
        self._tracks[f_key] = track             
            
        
        
    def scan_file_avprobe( self , file_name ):
        try:
            data_txt = subprocess.check_output( [ self.__ffprobe_cmd , "-show_format" , file_name ] , 
                                                stderr=subprocess.STDOUT , shell=False )
        except :
            data_txt = "ffprobe ERROR"
         
        if data_txt != "ffprobe ERROR" :
            try:
                data_txt = data_txt.decode(encoding='UTF-8')
            except:
                data_txt = data_txt.decode(encoding='ISO-8859-1')
                
        track = {} 
        ( foo , f_key ) = os.path.split( file_name )
        
        track['file_name'] = file_name
        
        re_flags = ( re.MULTILINE | re.IGNORECASE | re.UNICODE )
        
        m = re.search( r"(\[format].*)" , data_txt , re_flags | re.DOTALL )
        if m != None:
            format_tags = m.group(1)
        else:
            self._tracks[f_key] = None
            raise UnreadableAudioFileException( "problematic file: file_name" )   
        
        buf = StringIO.StringIO( format_tags )
        config = ConfigParser.ConfigParser()
        config.readfp(buf)
        
        
                     
        ##########################################
        # string examples:   
        #Audio: flac, 44100 Hz, stereo, s16
        #Stream #0:0(und): Audio: alac (alac / 0x63616C61), 44100 Hz, 2 channels, s16, 634 kb/s
        #Stream #0:0(und): Audio: aac (LC) (mp4a / 0x6134706D), 44100 Hz, stereo, fltp, 255 kb/s (default
        #Stream #0:0: Audio: flac, 44100 Hz, stereo, s16        
        m = re.search( r"Stream.*Audio:(.*)$" , data_txt , re_flags )
        if m != None:
            fmt = m.group(1)
            #print(fmt)
            
        fmt = re.split( "," , fmt )
        
        #print( fmt )
        track['codec'] = re.search( "\s*(\w+)" , fmt[0] , re_flags ).group(1)
        track['sampling_rate'] = re.search( "\s*(\d+)" , fmt[1] , re_flags ).group(1)
        track['channel'] = re.search( "^\s*([\S][\s|\S]*[\S])\s*$" , fmt[2] , re_flags ).group(1)
        
        m = re.search( "(\d+)" , fmt[3] , re_flags )
        if m != None:
            track['bit'] = m.group(1) 
        else :
            track['bit'] = "16"
            
        self._tracks[f_key] = track 
        

        

    def album_len( self ):
        return len( self._tracks )

    def get_album_cnt( self ):
        return len( self._album )
    
    def get_disk_nr(self):
        if len( self._disk_nr ) > 0 :
            return self._disk_nr[0]
        else :
            return None
    
    def get_album_list(self):
        return self._album

    def get_album_title( self ):

        if len( self._album ) > 1 :
            return "Various"
        elif len( self._album ) == 0 :
            return None
        else :
            for k in self._album.keys():
                res = k
            return res


    def track_unreadable_failure( self , file_name ):
        if self._tracks[file_name] == None :
            return True
        else :
            return False
            
    
    def get_album_sha1( self , title=None ):
        
        if title == None :
            p_title = self.get_album_title()
        else :
            p_title = title 
        
        key_string = ""
        key_string = key_string + str( p_title ) + str( self.get_album_artist() )
        
        for track in sorted ( self._tracks.keys() ) :
            
            if self._tracks[track] == None : 
                continue
            
            if not self._tracks[track].get( 'size' , False ) or not self._tracks[track].get( 'codec', False ) :
                continue
            
            if title != None and not self._tracks[track]["album"] != title :
                continue
            
            key_string = key_string + track 
            key_string = key_string + str( self._tracks[track]['size'] )
            key_string = key_string + str( self._tracks[track]['codec'] )
        
        return hashlib.sha1( bytearray( key_string.encode("utf8") ) ).hexdigest()
    
            
    def get_album_artist_old( self ):

        if len( self._artist ) > 1 :
            return "Various Artists"
        elif len( self._artist ) == 0 :
            return None
        else :
            for k in self._artist.keys():
                res = k
            return res
    
    
    def get_album_artist( self , album=None ):

        if album == None :
            return [ self.get_album_artist_old() ]

        artists = []
        for track in self._tracks.keys() :
            if track["album"] == album :
                if not track["artist"] in artists :
                    artists.append( track["artist"] )
        
        return artists 
    
    
    def get_value( self , file_name , field ):
        
        f = self._tracks.get( file_name , None )
        
        if f == None :
            return None
        
        return f.get( field , None )
        


        

