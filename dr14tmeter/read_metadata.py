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

from dr14tmeter.audio_decoder import AudioDecoder

# Test example !!!!!
# a = subprocess.check_output( [ "ffprobe" , "-show_format" , "/media/esterno_xfs/data/Musica/Musica/aavv/01-blitzkrieg_bop_160_lame_abr.mp3" ] , stderr=subprocess.STDOUT , shell=False )


class RetirveMetadata:
    
    def __init__( self ):
        self._album = {}
        self._artist = {}
        self._tracks = {}
    
    
    def scan_dir( self , dir_name , files_list=None ):
        
        self._album = {}
        self._tracks = {}
        self._artist = {}
        
        if files_list == None:
            dir_name = os.path.abspath( dir_name )
            files_list = sorted( os.listdir( dir_name ) )
        
        ad = AudioDecoder()
        
        for file_name in files_list :
            
            ( fn , ext ) = os.path.splitext( file_name )
            full_file = os.path.join( dir_name , file_name )
            
            if ext in ad.formats :
                self.scan_file( full_file )
                
        #print( self._tracks )
    
    
    def scan_file( self , file_name ):
        
        #print("")
        #print( file_name )
        
        try:
            data_txt = subprocess.check_output( [ "ffprobe" , "-show_format" , file_name ] , stderr=subprocess.STDOUT , shell=False )
        except :
            data_txt = "ffprobe ERROR"
         
        if data_txt != "ffprobe ERROR" :
            try:
                data_txt = data_txt.decode(encoding='UTF-8')
            except:
                data_txt = data_txt.decode(encoding='ISO-8859-1')
        
        track = {} 
        
        re_flags = ( re.MULTILINE | re.IGNORECASE | re.UNICODE )
        
        m = re.search( r"\s*track\s*\:\s*(\d+)$" , data_txt , re_flags )
        if m != None:
            track['nr'] = int( m.group(1) )
        
        m = re.search( r"\s*album\s*\:\s*(.*)$" , data_txt , re_flags )
        if m != None:
            #print( m.group(1) )
            self._album.setdefault( m.group(1) , 0 )
            self._album[m.group(1)] += 1
            
        m = re.search( r"\s*title\s*\:\s*(.*)$" , data_txt , re_flags )
        if m != None:
            track['title'] = m.group(1)
        
        m = re.search( r"\s*artist\s*\:\s*(.*)$" , data_txt , re_flags )
        if m != None:
            self._artist.setdefault( m.group(1) , 0 )
            self._artist[m.group(1)] += 1
        
        m = re.search( r"\s*genre\s*\:\s*(.*)$" , data_txt , re_flags )
        if m != None:
            track['genre'] = m.group(1)
         
        ##########################################
        # string examples:   
        #Audio: flac, 44100 Hz, stereo, s16
        #Stream #0:0(und): Audio: alac (alac / 0x63616C61), 44100 Hz, 2 channels, s16, 634 kb/s
        #Stream #0:0: Audio: flac, 44100 Hz, stereo, s16
        m = re.search( r"\:\s*Audio\s*\:\s*(\w+)[^,]*,\s*(\d*)\s*Hz\s*,\s*([\w\s]*)\s*,\s*s(\d+)" , data_txt , re_flags )
        if m != None:
            track['codec'] = m.group(1)
            track['s_rate'] = m.group(2)
            track['channel'] = m.group(3)
            track['bit'] = m.group(4)
            
            #print ( m.group(1) + " " + m.group(2)+ " " + m.group(3)+ " " + m.group(4) )
        
        m = re.search( r"\,\s*bitrate\s*\:\s*(\d*)\s*kb" , data_txt , re_flags )
        if m != None:
            track['bitrate'] = m.group(1)
            #print ( m.group(1) )
            
        ( foo , f_key ) = os.path.split( file_name )
        self._tracks[f_key] = track 
        


    def album_len( self ):
        return len( self._tracks )


    def get_album_title( self ):

        if len( self._album ) > 1 :
            return "Various"
        elif len( self._album ) == 0 :
            return None
        else :
            for k in self._album.keys():
                res = k
            return res

    
    def get_album_artist( self ):

        if len( self._artist ) > 1 :
            return "Various Artists"
        elif len( self._album ) == 0 :
            return None
        else :
            for k in self._artist.keys():
                res = k
            return res
    
    def get_value( self , file_name , field ):
        
        f = self._tracks.get( file_name , None )
        
        if f == None :
            return None
        
        return f.get( field , None )
        


        

