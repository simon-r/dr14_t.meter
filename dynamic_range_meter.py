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
            self.res_list.append( { 'file_name': file_name , 'dr14': dr14 , 'dB_peak': dB_peak , 'dB_rms': dB_rms } )
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
                res = { 'file_name': file_name , 'dr14': dr14 , 'dB_peak': dB_peak , 'dB_rms': dB_rms }
                self.res_list.append(res)
                
        return len( self.res_list )
 
    
    def write_dr14( self , tm ):
        txt = ''
        
        txt = tm.new_table(txt)
        for i in len( self.res_list ):
            txt = tm.new_row(txt)
            
            txt = tm.new_cell(txt)
            txt = txt + 'DR' + self.res_list[i]['dr14']
            txt = tm.end_cell(txt)
            
            txt = tm.new_cell(txt)
            txt = txt + self.res_list[i]['dB_peak'] + ' dB'
            txt = tm.end_cell(txt)
            
            txt = tm.new_cell(txt)
            txt = txt + self.res_list[i]['dB_rms'] + ' dB'
            txt = tm.end_cell(txt)
            
            txt = tm.new_cell(txt)
            txt = txt + self.res_list[i]['file_name']
            txt = tm.end_cell(txt)
            
            txt = tm.end_row(txt)
        txt = tm.end_table()
        
        sel.table_txt = txt
        return txt 
    
    
    
    
class Table:
    def new_table( self , txt ):
        pass
    
    def end_table( self , txt ):
        pass
    
    def new_rox( self , txt ):
        pass
    
    def end_row( self , txt ):
        pass
    
    def new_cell( self , txt ):
        pass
    
    def end_cell( self , txt ):
        pass
    
    
    
class TextTable ( Table ):

    def new_table( self , txt ):
        return txt + '\n\r'
    
    def end_table( self , txt ):
        return txt + '\n\r'
    
    def new_rox( self , txt ):
        return txt + '\n\r'
    
    def end_row( self , txt ):
        return txt + '\n\r'
    
    def new_cell( self , txt ):
        return txt + ''
    
    def end_cell( self , txt ):
        return txt + '\t'
    
    
class BBcodeTable ( Table ):

    def new_table( self , txt ):
        return txt + '[table]\n\r'
    
    def end_table( self , txt ):
        return txt + '[/table]\n\r'
    
    def new_rox( self , txt ):
        return txt + '[tr]\n\r'
    
    def end_row( self , txt ):
        return txt + '[/tr]\n\r'
    
    def new_cell( self , txt ):
        return txt + '[th]'
    
    def end_cell( self , txt ):
        return txt + '[/th]\t'
    
   