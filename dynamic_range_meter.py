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
from compute_dr14 import compute_dr14
from audio_track import *
import sys



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
             
        self.dr14 = int( round( self.dr14 / len( self.res_list ) ) )
        return len( self.res_list )
 
    
    def write_dr14( self , tm ):
        txt = ''
        
        txt = txt + " --------------------------------------------------------------------------------- " + tm.nl()
        txt = tm.new_bold(txt)
        txt = txt + " Analyzed folder:  " + self.dir_name + tm.nl()
        txt = tm.end_bold(txt)
        txt = txt + " --------------------------------------------------------------------------------- " + tm.nl()
        
        txt = tm.new_table(txt)
        txt = tm.append_row( txt , [ "-----------", "-----------", "-----------", "-------------------------------" ] )
        txt = tm.append_row( txt , [ "DR", "Peak", "RMS", "File name" ] )
        txt = tm.append_row( txt , [ "-----------", "-----------", "-----------", "-------------------------------" ] )
        
        for i in range( len( self.res_list ) ) :
            
            row = []
            row.append( "DR%d" % self.res_list[i]['dr14'] )
            row.append( " %.2f" % self.res_list[i]['dB_peak'] + ' dB' )
            row.append( " %.2f" % self.res_list[i]['dB_rms'] + ' dB' )
            row.append( self.res_list[i]['file_name'] )
            
            txt = tm.append_row( row )

        
        txt = tm.append_row( txt , [ "-----------", "-----------", "-----------", "-------------------------------" ] )
        
        txt = tm.end_table(txt)
        
        
        txt = txt + tm.nl()
        txt = txt + "Number of files:	  " + str(len( self.res_list )) + tm.nl()
        txt = txt + tm.nl()
        txt = txt + "Official DR value:	  " + str(self.dr14) + tm.nl()
        txt = txt + tm.nl()
        txt = txt + "=============================================================================================="
        txt = txt + tm.nl()
        
        
        self.table_txt = txt
        return txt 
    
    def fwrite_dr14( self , file_name , tm ):
        self.write_dr14( tm )
        out_file = open( file_name , "wt")
        out_file.write( self.table_txt )
        out_file.close() 
    
    
    
class Table:
    
    def nl(self):
        if sys.platform.startswith('linux'):
            return '\n'
        elif sys.platform.startswith('win'):
            return '\n\r'
    
    def append_row( self , txt , row_el ):
        txt = self.new_row(txt)
        for i in row_el:
            txt = self.new_cell(txt)
            txt = txt + i
            txt = self.end_cell(txt)
        txt = self.end_row(txt)
        return txt

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
    
    def new_bold( self , txt ):
        pass
    
    def end_bold( self , txt ):
        pass
    
    
    
class TextTable ( Table ):

    def new_table( self , txt ):
        return txt + self.nl()
    
    def end_table( self , txt ):
        return txt + self.nl()
    
    def new_row( self , txt ):
        return txt + ''
    
    def end_row( self , txt ):
        return txt + self.nl()
    
    def new_cell( self , txt ):
        return txt + ''
    
    def end_cell( self , txt ):
        return txt + '\t'
    
    def new_bold( self , txt ):
        return txt + ''
    
    def end_bold( self , txt ):
        return txt + ''
    
    
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
        return txt + '[/th]'
    
    def new_bold( self , txt ):
        return txt + '[b]'
    
    def end_bold( self , txt ):
        return txt + '[/b]'