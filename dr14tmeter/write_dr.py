# dr14_t.meter: compute the DR14 value of the given audiofiles
# Copyright (C) 2011 - 2012  Simone Riva
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
import dr14tmeter.dr14_global as dr14
import dr14tmeter.table as table

class WriteDr :
    
    def __init__(self):
        self.__dr_database_compatible = True
    
    def set_dr_database( self , f ):
        self.__dr_database_compatible = f
        
    def get_dr_database(self):
        return self.__dr_database_compatible
    
    def write_dr( self , drm , tm ):
        txt = ""
        
        ( head , album_dir ) = os.path.split( drm.dir_name )
        
        txt = tm.new_table(txt)
        
        txt = tm.new_head( txt )
        
        txt = tm.append_separator_line( txt )
        txt = tm.add_title( txt , " Analyzed folder:  " + album_dir )
        
        txt = tm.end_head( txt )
        
        txt = tm.new_tbody( txt )
        
        txt = tm.append_separator_line( txt )
        txt = tm.append_row( txt , [ " DR", "Peak", "RMS", "Duration" , "File name" ] , 'h' )
        txt = tm.append_separator_line( txt )
        
        for i in range( len( drm.res_list ) ) :
            
            if drm.res_list[i]['dr14'] > dr14.min_dr() :
                row = []
                row.append( " DR%d" % drm.res_list[i]['dr14'] )
                row.append( " %.2f" % drm.res_list[i]['dB_peak'] + ' dB' )
                row.append( " %.2f" % drm.res_list[i]['dB_rms'] + ' dB' )
                row.append( " %s" % drm.res_list[i]['duration'] )
                row.append( " %s" % drm.res_list[i]['file_name'] )
            
                txt = tm.append_row( txt , row )

        txt = tm.end_tbody( txt )
        
        txt = tm.new_foot( txt )
        txt = tm.append_separator_line( txt )
               
        txt = tm.add_title( txt , "Number of files:    " + str(len( drm.res_list )) )
        txt = tm.add_title( txt , "Official DR value:  DR%d" % int(drm.dr14) )
        
        txt = tm.append_empty_line( txt )
        txt = tm.add_title( txt , "Dr14 T.meter %s " % dr14.dr14_version() )
        
        txt = tm.append_closing_line( txt )
        txt = tm.end_foot( txt )
        
        txt = tm.end_table(txt)
        
        return txt 
    

class WriteDrExtended( WriteDr ) :

    def __init__(self):
        WriteDr.__init__(self)

    def write_dr( self , drm , tm ):
        txt = ""
         
        ( head , album_dir ) = os.path.split( drm.dir_name )
        
        txt = tm.new_table( txt )
        
        txt = tm.new_head( txt )
        txt = tm.append_separator_line( txt )
        
        album_t = drm.meta_data.get_album_title()
        artist = drm.meta_data.get_album_artist()
        
        if not isinstance( tm , table.TextTable ) :
            self.set_dr_database( False )
        
        if self.get_dr_database() :
        
            title = "" 
            
            if album_t == None :
                title = " Analyzed folder:  " + album_dir 
            else:
                title = " Analyzed: " + album_t 
                if artist != None :
                    title = title + " /  Artist: " + artist
            txt = tm.add_title( txt , title )
        
        else:
        
            if album_t == None :
                txt = tm.add_title( txt , " Analyzed folder:  " + album_dir )
            else:
                txt = tm.add_title( txt , " Album: " + album_t )
                if artist != None :
                    txt = tm.add_title( txt , " Artist: " + artist )
            
        
        txt = tm.end_head( txt )
        
        txt = tm.new_tbody( txt )
        
        txt = tm.append_separator_line( txt )
        txt = tm.append_row( txt , [ "DR", "Peak", "RMS", "Duration" , "Title [codec]" ] , 'h' )
        txt = tm.append_separator_line( txt )
        
        list_bit = []
        
        sum_kbs = 0
        cnt = 0
        
        sampl_rate = []
        
        d_nr = 0 ;        
        
        
        for i in range( len( drm.res_list ) ) :
            
            if drm.res_list[i]['dr14'] > dr14.min_dr() :
                row = []
                row.append( " DR%d" % drm.res_list[i]['dr14'] )
                row.append( " %.2f" % drm.res_list[i]['dB_peak'] + ' dB' )
                row.append( " %.2f" % drm.res_list[i]['dB_rms'] + ' dB' )
                row.append( drm.res_list[i]['duration'] )
                
                #print( "> " + drm.res_list[i]['file_name'] )
                
                curr_file_name = drm.res_list[i]['file_name']
                
                tr_title = drm.meta_data.get_value( curr_file_name , 'title' )
                #print( "> " + tr_title )
                if tr_title == None :
                    row.append( drm.res_list[i]['file_name'] )
                else:
                    nr = drm.meta_data.get_value( curr_file_name , 'nr' )
                    codec = drm.meta_data.get_value( curr_file_name , 'codec' )
                    
                    if nr == None :
                        nr = i + 1
                    
                    row.append( "%02d - %s \t [%s]" % ( nr , tr_title , codec ) )
                    
                bitrate = drm.meta_data.get_value( curr_file_name , 'bitrate' )
                bit = drm.meta_data.get_value( curr_file_name , 'bit' )
                s_rate = drm.meta_data.get_value( curr_file_name , 's_rate' )
                
                kbs = drm.meta_data.get_value( curr_file_name , 'bitrate' )
                
                if kbs != None :
                    sum_kbs += int( kbs )
                    cnt = cnt + 1
                    
                if bit not in list_bit :
                    list_bit.append( bit )    
                        
                if s_rate not in sampl_rate :
                    sampl_rate.append( s_rate )
                    
                txt = tm.append_row( txt , row )
        
        txt = tm.end_tbody( txt )
        
        txt = tm.new_foot( txt )
        txt = tm.append_separator_line( txt )
               
        txt = tm.add_title( txt , " Number of files:    " + str(len( drm.res_list )) )
        txt = tm.add_title( txt , " Official DR value:  DR%d" % int(drm.dr14) )
        
        txt = tm.append_empty_line( txt )
        
        txt = tm.add_title( txt , " Sampling rate: \t\t %s Hz" % sampl_rate[0] )
        
        if cnt > 0:
            txt = tm.add_title( txt , " Average bitrate: \t\t %dkbs " % ( sum_kbs / cnt )  )
        
        mf_bit = max( set( list_bit ) , key=list_bit.count )
        txt = tm.add_title( txt , " Bits per sample: \t\t %s bit" % ( mf_bit ) )
        
        txt = tm.append_empty_line( txt )
        txt = tm.add_title( txt , "Dr14 T.meter %s " % dr14.dr14_version() )
        
        txt = tm.append_closing_line( txt )
        txt = tm.end_foot( txt )
        
        txt = tm.end_table(txt)
        
        return txt

 