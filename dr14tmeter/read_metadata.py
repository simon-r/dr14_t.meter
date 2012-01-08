import subprocess
import sys
import os
import re

from dr14tmeter.audio_decoder import AudioDecoder

# Test example !!!!!
# a = subprocess.check_output( [ "ffprobe" , "-show_format" , "/media/esterno_xfs/data/Musica/Musica/aavv/01-blitzkrieg_bop_160_lame_abr.mp3" ] , stderr=subprocess.STDOUT , shell=False )


class RetirveMetadata:
    
    def __init__( self ):
        pass
    
    
    def scan_dir( self , dir_name , dir_list=None ):
        
        self._album = {}
        self._traks = {}
        
        if dir_list == None:
            dir_name = os.path.abspath( dir_name )
            dir_list = sorted( os.listdir( dir_name ) )
        
        ad = AudioDecoder()
        
        for file_name in dir_list :
            
            ( fn , ext ) = os.path.splitext( file_name )
            full_file = os.path.join( dir_name , file_name )
            
            if ext in ad.formats :
                self.scan_file( full_file )
    
    
    def scan_file( self , file_name ):
        
        data_txt = subprocess.check_output( [ "ffprobe" , "-show_format" , file_name ] , stderr=subprocess.STDOUT , shell=False )
        data_txt = data_txt.decode()
        
        print("")
        print( file_name )
        
        track = {} 
        
        re_flags = ( re.MULTILINE | re.IGNORECASE )
        
        m = re.search( r"\s*track\s*\:\s*(\d+)$" , data_txt , re_flags )
        if m != None:
            track['nr'] = m.group(1) 
        
        m = re.search( r"\s*album\s*\:\s*(.*)$" , data_txt , re_flags )
        if m != None:
            self._album.setdefault( m.group(1) , 0 )
            _album[m.group(1)] += 1
        
        m = re.search( r"\s*title\s*\:\s*(.*)$" , data_txt , re_flags )
        if m != None:
            track['title'] = m.group(1) 
        
        #Audio: flac, 44100 Hz, stereo, s16
        m = re.search( r"\:\s*Audio\s*\:\s*(\w*)\s*,\s*(\d*)\s*Hz\s*,\s*(\w*)\s*,\s*s(\d+)" , data_txt , re_flags )
        if m != None:
            track['codec'] = m.group(1)
            track['s_rate'] = m.group(2)
            track['channel'] = m.group(3)
            track['bit'] = m.group(4)
            
            #print ( m.group(1) + " " + m.group(2)+ " " + m.group(3)+ " " + m.group(4) )
        
        m = re.search( r"\,\s*bitrate\s*\:\s*(\d*)\s*kb" , data_txt , re_flags )
        if m != None:
            track['bitrate'] = m.group(1)
            print ( m.group(1) )
            
        self._tracks.append( track )
        



