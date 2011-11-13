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
        self.dr14 = 0 
        
        at = AudioTrack() 
        for file_name in dir_list:
            full_file = os.path.join( dir_name , file_name )
            
            if at.open( full_file ):
                ( dr14, dB_peak, dB_rms ) = compute_dr14( at.Y , at.Fs )
                self.dr14 = self.dr14 + dr14
                res = { 'file_name': file_name , 'dr14': dr14 , 'dB_peak': dB_peak , 'dB_rms': dB_rms }
                self.res_list.append(res)
             
        self.dr14 = round( self.dr14 / len( self.res_list ) )
        return len( self.res_list )
 
    
    def write_dr14( self , tm ):
        txt = ''
        
        txt = txt + " --------------------------------------------------------------------------------- " + "\n\r"
        txt = txt + " Analyzed folder:  " + self.dir_name + "\n\r"
        txt = txt + " --------------------------------------------------------------------------------- " + "\n\r"
        
        txt = tm.new_table(txt)
        
        txt = tm.new_row(txt)
        
        txt = tm.new_cell(txt)
        txt = txt + "-----------"
        txt = tm.end_cell(txt)
        
        txt = tm.new_cell(txt)
        txt = txt + "-----------"
        txt = tm.end_cell(txt)
        
        txt = tm.new_cell(txt)
        txt = txt + "-----------"
        txt = tm.end_cell(txt)
        
        txt = tm.new_cell(txt)
        txt = txt + "-------------------------------"
        txt = tm.end_cell(txt)
        
        txt = tm.end_row(txt)
        
        for i in range( len( self.res_list ) ) :
            txt = tm.new_row(txt)
            
            txt = tm.new_cell(txt)
            txt = txt + "DR%d" % self.res_list[i]['dr14']
            txt = tm.end_cell(txt)
            
            txt = tm.new_cell(txt)
            txt = txt + " %.2f" % self.res_list[i]['dB_peak'] + ' dB'
            txt = tm.end_cell(txt)
            
            txt = tm.new_cell(txt)
            txt = txt + " %.2f" % self.res_list[i]['dB_rms'] + ' dB'
            txt = tm.end_cell(txt)
            
            txt = tm.new_cell(txt)
            txt = txt + self.res_list[i]['file_name']
            txt = tm.end_cell(txt)
            
            txt = tm.end_row(txt)
            
            txt = tm.new_row(txt)
        
        
        txt = tm.new_cell(txt)
        txt = txt + "-----------"
        txt = tm.end_cell(txt)
        
        txt = tm.new_cell(txt)
        txt = txt + "-----------"
        txt = tm.end_cell(txt)
        
        txt = tm.new_cell(txt)
        txt = txt + "-----------"
        txt = tm.end_cell(txt)
        
        txt = tm.new_cell(txt)
        txt = txt + "-------------------------------"
        txt = tm.end_cell(txt)
        
        txt = tm.end_row(txt)        
        
        txt = tm.end_table(txt)
        
        
        txt = txt + "\n\r\n\r"
        txt = txt + "Number of files:	  " + str(len( self.res_list )) + "\n\r"
        txt = txt + "\n\r\n\r"
        txt = txt + "Official DR value:	  " + str(self.dr14) + "\n\r"
        txt = txt + "\n\r\n\r"
        txt = txt + "=============================================================================================="
        txt = txt + "\n\r"
        
        
        self.table_txt = txt
        return txt 
    
    def fwrite_dr14( self , file_name , tm ):
        self.write_dr14( tm )
        out_file = open( file_name , "wt")
        out_file.write( self.table_txt )
        out_file.close() 
    
    
    
class Table:
    def new_table( self , txt ):
        pass
    
    def end_table( self , txt ):
        pass
    
    def new_row( self , txt ):
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
    
    def new_row( self , txt ):
        return txt + '\n\r'
    
    def end_row( self , txt ):
        return '\n\r' + txt + '\n\r'
    
    def new_cell( self , txt ):
        return txt + ''
    
    def end_cell( self , txt ):
        return txt + '\t'
    
    
class BBcodeTable ( Table ):

    def new_table( self , txt ):
        return txt + '[table]\n\r'
    
    def end_table( self , txt ):
        return txt + '[/table]\n\r'
    
    def new_row( self , txt ):
        return txt + '[tr]\n\r'
    
    def end_row( self , txt ):
        return txt + '\n\r[/tr]\n\r'
    
    def new_cell( self , txt ):
        return txt + '[th]'
    
    def end_cell( self , txt ):
        return txt + '[/th]\t'
    
   