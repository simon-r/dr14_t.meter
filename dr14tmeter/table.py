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


import os
import sys


class Table:
    
    def nl(self):
        if sys.platform.startswith('linux') or sys.platform.startswith('darwin'):
            return '\n'
        elif sys.platform.startswith('win'):
            return '\n\r'
    
    def append_row( self , txt , row_el , cell_type='d'):
        
        if cell_type == 'd':
            n_cell = self.new_cell
            e_cell = self.end_cell
        elif cell_type == 'h':
            n_cell = self.new_hcell
            e_cell = self.end_hcell
        
        txt = self.new_row(txt)
        
        for i in row_el:
            txt = n_cell(txt)
            txt = txt + i
            txt = e_cell(txt)
            
        txt = self.end_row(txt)
        return txt

    def col_cnt( self ):
        return 5

    def append_separator_line( self , txt ):
        return txt
    
    def append_closing_line( self , txt ):
        return txt
        
    def append_empty_line( self , txt ):
        return self.append_row( txt , [ "", "", "", "", "" ] )

    def add_title( self , txt , title ):
        NotImplementedError(" %s : is virutal and must be overridden." % sys._getframe().f_code.co_name )
    
    def new_table( self , txt ):
        NotImplementedError(" %s : is virutal and must be overridden." % sys._getframe().f_code.co_name )
    
    def end_table( self , txt ):
        NotImplementedError(" %s : is virutal and must be overridden." % sys._getframe().f_code.co_name )
    
    def new_head( self , txt ):
        return txt
    
    def end_head( self , txt ):
        return txt
    
    def new_tbody( self , txt ):
        return txt
    
    def end_tbody( self , txt ):
        return txt
    
    def new_foot( self , txt ):
        return txt
    
    def end_foot( self , txt ):
        return txt
    
    def new_row( self , txt ):
        NotImplementedError(" %s : is virutal and must be overridden." % sys._getframe().f_code.co_name )
    
    def end_row( self , txt ):
        NotImplementedError(" %s : is virutal and must be overridden." % sys._getframe().f_code.co_name )
    
    def new_cell( self , txt ):
        NotImplementedError(" %s : is virutal and must be overridden." % sys._getframe().f_code.co_name )
    
    def end_cell( self , txt ):
        NotImplementedError(" %s : is virutal and must be overridden." % sys._getframe().f_code.co_name )
    
    def new_hcell( self , txt ):
        return self.new_cell( txt )
    
    def end_hcell( self , txt ):
        return self.end_cell( txt )
    
    def new_bold( self , txt ):
        NotImplementedError(" %s : is virutal and must be overridden." % sys._getframe().f_code.co_name )
    
    def end_bold( self , txt ):
        NotImplementedError(" %s : is virutal and must be overridden." % sys._getframe().f_code.co_name )
    
    
    

class TextTable ( Table ):

    def append_separator_line( self , txt ):
        return self.append_row( txt , [ "----------------------------------------------------------------------------------------------" ] )

    def append_closing_line( self , txt ):
        return self.append_row( txt , [ "==============================================================================================" ] )
    
    def append_empty_line( self , txt ):
        return self.append_row( txt , [ "" ] ) 

    def add_title( self , txt , title ):
        return txt + title + self.nl()

    def new_table( self , txt ):
        return txt
    
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

    def append_separator_line( self , txt ):
        return self.append_row( txt , [ "-----------", "-----------", "-----------", "-----------", "-------------------------------" ] )

    def append_closing_line( self , txt ):
        return self.append_row( txt , [ "===========", "===========", "===========", "===========", "===============================" ] )

    def add_title( self , txt , title ):
        return txt + self.nl() + "[tr]" + self.nl() + " [td  colspan=%d] " % self.col_cnt() + title + " [/td] " + self.nl() + "[/tr]" + self.nl()

    def new_table( self , txt ):
        return txt + '[table]' + self.nl()
    
    def end_table( self , txt ):
        return txt + self.nl() + '[/table]' + self.nl() 
    
    def new_row( self , txt ):
        return txt + self.nl() + '[tr]' + self.nl()
    
    def end_row( self , txt ):
        return txt + self.nl() + '[/tr]' + self.nl()
    
    def new_cell( self , txt ):
        return txt + ' [td]'
    
    def end_cell( self , txt ):
        return txt + '[/td]'
    
    def new_bold( self , txt ):
        return txt + '[b]'
    
    def end_bold( self , txt ):
        return txt + '[/b]'


class HtmlTable ( Table ):

    def add_title( self , txt , title ):
        return txt + self.nl() + "<tr>" + self.nl() + " <th colspan=\"%d\" > " % self.col_cnt() + title + "</th>" + self.nl() + "</tr>" + self.nl() 

    def new_table( self , txt ):
        return txt + "<table>" + self.nl() 
    
    def end_table( self , txt ):
        return txt + self.nl() + "</table>" + self.nl()
        
    def new_head( self , txt ):
        return txt + self.nl() + "<thead>" + self.nl() 
    
    def end_head( self , txt ):
        return txt + self.nl() + "</thead>" + self.nl()
        
    def new_tbody( self , txt ):
        return txt + self.nl() + "<tbody>" + self.nl() 
    
    def end_tbody( self , txt ):
        return txt + self.nl() + "</tbody>" + self.nl() 
    
    def new_foot( self , txt ):
        return txt + self.nl() + "<tfoot>" + self.nl() 
    
    def end_foot( self , txt ):
        return txt + self.nl() + "</tfoot>" + self.nl() 
    
    def new_row( self , txt ):
        return txt + self.nl() + "<tr>" + self.nl() 
    
    def end_row( self , txt ):
        return txt + self.nl() + "</tr>" + self.nl() 
    
    def new_cell( self , txt ):
        return txt + ' <td>'
    
    def end_cell( self , txt ):
        return txt + '</td>'
    
    def new_hcell( self , txt ):
        return txt + ' <th>'
    
    def end_hcell( self , txt ):
        return txt + '</th>'
    
    def new_bold( self , txt ):
        return txt + '<b>'
    
    def end_bold( self , txt ):
        return txt + '</b>'


class MediaWikiTable ( Table ):

    def add_title( self , txt , title ):
        return txt + "|-" + self.nl() + "!align=\"left\" colspan=\"%d\" | " % self.col_cnt() + title + self.nl()

    def new_table( self , txt ):
        return txt + "{| " + self.nl() 
    
    def end_table( self , txt ):
        return txt + "|}" + self.nl()
        
    def new_row( self , txt ):
        return txt + "|-" + self.nl() 
    
    def end_row( self , txt ):
        return txt + self.nl()
    
    def new_cell( self , txt ):
        return txt + '||'
    
    def end_cell( self , txt ):
        return txt
        
    def new_bold( self , txt ):
        return txt + "\'\'\'"
    
    def end_bold( self , txt ):
        return txt + "\'\'\'"

