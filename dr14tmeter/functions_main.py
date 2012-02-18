
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
    

import os
from optparse import OptionParser
import time
import multiprocessing
from dr14tmeter.dynamic_range_meter import DynamicRangeMeter
from dr14tmeter.table import *
from dr14tmeter.dr14_global import dr14_version, TestVer, test_new_version, get_home_url, get_new_version
import subprocess
import sys
import re


def list_rec_dirs( basedir , subdirlist=None ):
    
    if subdirlist == None :
        subdirlist = []
        subdirlist.append( basedir )
        

    for item in os.listdir( basedir ):
        item = os.path.join( basedir , item )
        if os.path.isdir( item ):
            item = os.path.abspath( item )
            #print( item )
            subdirlist.append( item )
            list_rec_dirs( item , subdirlist )
            
    return subdirlist
        

def write_results( dr , options , out_dir , cur_dir ) :
    out_list = "" ;
    
    table_format = not( options.basic_table )    
    
    if out_dir == None :
        full_out_dir = os.path.join( cur_dir )
    else :
        full_out_dir = out_dir
        
    if options.print_std_out :
        dr.fwrite_dr( "" , TextTable() , table_format , True )
        
    if options.turn_off_out :
        return 
    
    if 'b' in options.out_tables:
        dr.fwrite_dr( os.path.join( full_out_dir , "dr14_bbcode.txt" ) , BBcodeTable() , table_format )
        out_list = " dr14_bbcode.txt "
        
    if 't' in options.out_tables:
        dr.fwrite_dr( os.path.join( full_out_dir , "dr14.txt" ) , TextTable() , table_format )
        out_list = out_list + " dr14.txt "
        
    if 'h' in options.out_tables:
        dr.fwrite_dr( os.path.join( full_out_dir , "dr14.html" ) , HtmlTable() , table_format )
        out_list = out_list + " dr14.html "
        
    print( "DR = " + str( dr.dr14 ) )

    print("")
    print("- The full result has been written in the files: %s" % out_list )
    print("- located in the directory: ")
    print( full_out_dir )
    print("")



def parse_args():
    desc = "Compute the DR14 value of the audio files according to the algorithm " 
    desc =  desc + "described by the Pleasurize Music Foundation "
    desc =  desc + "Visit: http://www.dynamicrange.de/"

    use = "usage: %prog [options] path_name"

    parser = OptionParser( description=desc ,  usage=use  , version="%prog " + dr14_version()  )

    parser.add_option("-m", "--multithread",
        action="store_true",
        dest="multithread",
        default=False,
        help="Uses the multi-Core mode")

    parser.add_option("-f", "--file",
        action="store_true",
        dest="scan_file",
        default=False,
        help="Compute the DR14 of a single file and exit")
    
    parser.add_option("-r", "--recursive",
        action="store_true",
        dest="recursive",
        default=False,
        help="Scan recursively the subdirectories")

    parser.add_option("-b", "--basic_table",
        action="store_true",
        dest="basic_table",
        default=False,
        help="Write the resulting tables in the basic format")

    parser.add_option("-n", "--turn_off_out",
        action="store_true",
        dest="turn_off_out",
        default=False,
        help="do not writes the output files")

    parser.add_option("-p", "--print_std_out",
        action="store_true",
        dest="print_std_out",
        default=False,
        help="writes the full result on the std_out")

    parser.add_option("-o", "--outdir",
        action="store",
        dest="out_dir",
        type="string" ,
        default="" ,
        help="Write the resultings files into the given directory")
    
    parser.add_option("-t", "--tables",
        action="store",
        dest="out_tables",
        type="string" ,
        default="thb" ,
        help="Select the output files to be written, codes: h=html t=text b=bbcode ")

    (options, args) = parser.parse_args()
    
    if len(args) <= 0:
        parser.error("wrong number of arguments")
        exit( 1 )
    
    return (options, args) 