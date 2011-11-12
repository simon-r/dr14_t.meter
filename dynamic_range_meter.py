import read_wav
import os
from compute_dr14 import compute_dr14
from audio_track import *


class DynamicRangeMeter:
    
    def scan_file( self , file_name):
        self.res_list = []
        self.dir_name = ''
        at = AudioTrack() 
        
        if at.open( file_name ):
            ( dr14 , peak , rms ) = compute_dr14.compute_dr14( Y , Fs )
            self.res_list[len(self.res_list):] = [[ file_name , dr14 , dB_peak , dB_rms ]]
            return 1
        else:
            return 0
        
    def scan_dir( self , dir_name ):
        dir_list = sorted( os.listdir( dir_name ) )
        
        self.res_list = []
        self.dir_name = dir_name 
        
        at = AudioTrack() 
        for file_name in dir_list:
            full_file = os.path.join( dir_name , file_name )
            
            if at.open( full_file ):
                ( dr14, dB_peak, dB_rms ) = compute_dr14( at.Y , at.Fs )
                self.res_list[len(self.res_list):] = [[ file_name , dr14 , dB_peak , dB_rms ]]
                
        return len( self.res_list )
    