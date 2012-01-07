import subprocess
import sys
import os
import re

from dr14tmeter.audio_decoder import AudioDecoder

# Test example !!!!!
# a = subprocess.check_output( [ "ffprobe" , "-show_format" , "/media/esterno_xfs/data/Musica/Musica/aavv/01-blitzkrieg_bop_160_lame_abr.mp3" ] , stderr=subprocess.STDOUT , shell=False )


class retirve_metadata:
    
    def __init__( self ):
        pass
    
    
    
    def scan_dir( self , dir_name ):
        
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
        
        re_flags = (re.MULTILINE | re.IGNORECASE)
        
        m = re.search( r"\s*album\s*\:\s*(.*)$" , data_txt , re_flags )
        if m != None:
            print ( m.group(1) )
        
        m = re.search( r"\s*title\s*\:\s*(.*)$" , data_txt , re_flags )
        if m != None:
            print ( m.group(1) )
        
        m = re.search( r"\:\s*Audio\s*\:\s*(\w*)" , data_txt , re_flags )
        if m != None:
            print ( m.group(1) )
        
        m = re.search( r"\,\s*bitrate\s*\:\s*(\d*)\s*kb" , data_txt , re_flags )
        if m != None:
            print ( m.group(1) )