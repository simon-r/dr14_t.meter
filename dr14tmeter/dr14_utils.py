
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
import argparse
import time
import multiprocessing
from dr14tmeter.dynamic_range_meter import DynamicRangeMeter
from dr14tmeter.table import *
from dr14tmeter.dr14_global import dr14_version, TestVer, test_new_version, get_home_url, get_new_version
import subprocess
import sys
import re
import tempfile
from dr14tmeter.out_messages import print_msg


def list_rec_dirs( basedir , subdirlist=None ):
    
    if subdirlist == None :
        subdirlist = []
        subdirlist.append( basedir )
        

    for item in os.listdir( basedir ):
        item = os.path.join( basedir , item )
        if os.path.isdir( item ):
            item = os.path.abspath( item )
            #print_msg( item )
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
    
    print_msg( "DR = " + str( dr.dr14 ) )
    
    if not ( os.access( full_out_dir , os.W_OK ) ) :
        full_out_dir = tempfile.gettempdir() ; 
        print_msg( "--------------------------------------------------------------- " )
        print_msg( "- ATTENTION !" )
        print_msg( "- You don't have the write permission for the directory: %s " % full_out_dir )
        print_msg( "- The result files will be written in the tmp dir: %s " % full_out_dir )
        print_msg( "--------------------------------------------------------------- " )
           
    
    if options.print_std_out :
        dr.fwrite_dr( "" , TextTable() , table_format , True )
        
    if options.turn_off_out :
        return 
    
    all_tables = False
    if 'a' in options.out_tables:
        all_tables = True 
    
    tables_list = { 'b' : ["dr14_bbcode.txt",BBcodeTable()] , 't' : ["dr14.txt",TextTable()]  ,
        'h' : ["dr14.html",HtmlTable()] , 'w' : ["dr14_mediawiki.txt",MediaWikiTable()] }
    
    out_list = ""
    
    
    for code in tables_list.keys():
        if code in options.out_tables or all_tables :
            dr.fwrite_dr( os.path.join( full_out_dir , tables_list[code][0] ) , tables_list[code][1] , table_format , append=options.append , dr_database=options.dr_database )
            out_list = out_list + " %s " % tables_list[code][0]
            
    
    print_msg("")
    print_msg("- The full result has been written in the files: %s" % out_list )
    print_msg("- located in the directory: ")
    print_msg( full_out_dir )
    print_msg("")



def parse_args():
    desc = "Compute the DR14 value of the audio files according to the algorithm " 
    desc =  desc + "described by the Pleasurize Music Foundation "
    desc =  desc + "Visit: http://www.dynamicrange.de/"

    parser = argparse.ArgumentParser( description=desc , version="%(prog)s " + dr14_version()  )


    parser.add_argument("-1", "--disable_multithread",
        action="store_true",
        dest="disable_multithread",
        help="Disable the multi-Core mode")
    
    parser.add_argument("-r", "--recursive",
        action="store_true",
        dest="recursive",
        help="Scan recursively the subdirectories")

    parser.add_argument("-a", "--append",
        action="store_true",
        dest="append",
        help="Append all results in a single file; it should be used in couple with -r")

    parser.add_argument("-b", "--basic_table",
        action="store_true",
        dest="basic_table",
        help="Write the resulting tables in the basic format")

    parser.add_argument("-n", "--turn_off_out",
        action="store_true",
        dest="turn_off_out",
        help="do not writes the output files")

    parser.add_argument("-p", "--print_std_out",
        action="store_true",
        dest="print_std_out",
        help="writes the full result on the std_out")

    parser.add_argument("-o", "--outdir",
        action="store",
        dest="out_dir",
        type=str,
        help="Write the resultings files into the given directory")
    
    parser.add_argument("-t", "--tables",
        action="store",
        choices = 'htbwa',
        dest="out_tables",
        default="t" ,
        help="Select the output files to be written. h=html t=text b=bbcode w=mediawiki a=all_formats")

    parser.add_argument("-d", "--dr_database",
        action="store_false",
        dest="dr_database",
        help="Output file compatible with the DR database at http:///www.dr.loudness-war.info" )

    parser.add_argument( "--hist" ,
        action="store_true",
        dest="histogram" ,
        help="Plot the histogram of dynamic of a single file and exit (beta)" )
    
    parser.add_argument("-f", "--file",
        action='store_true',
        dest="scan_file",
        help="Compute the DR14 of a single file and exit")

    parser.add_argument("--quiet",
        action="store_true",
        dest="quiet",
        help="Quite mode")

    parser.add_argument(
        dest="path_name",
        nargs='?',
        default='.'
        )
    
    return parser.parse_args()
