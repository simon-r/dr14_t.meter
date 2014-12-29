#!/usr/bin/python

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
import time
import multiprocessing
from dr14tmeter.parse_args import parse_args
from dr14tmeter.dynamic_range_meter import DynamicRangeMeter
from dr14tmeter.table import *
from dr14tmeter.audio_analysis import *
from dr14tmeter.database import dr_database
from dr14tmeter.dr14_global import dr14_version, TestVer, test_new_version, get_home_url, get_new_version, get_exe_name, test_hist_modules, test_compress_modules
import subprocess
import inspect
import sys
import re
from dr14tmeter.dr14_utils import *
from dr14tmeter.out_messages import *
import logging
import numpy

    
def main():
        
#===============================================================================
#     db = dr_database()
#     #db.build_database()
#     for i in range(10):
#         print( db.query("select * from Codec where name = \'mp3\' " ) )
#     
#     db.open_insert_session()
#     db.insert_track( "3533fdedcf6dcc81df2a8fd8b5bf90997d30cf9f" , "ciao" , 
#                      20 , 2.0 , 2.0 , 33.0 , 
#                      "mp3" , "3533fdedcf6dcc81df2a8fd8b5bf90997d30cf4f" , "meo" , "bob" )
# 
#     db.insert_track( "3533fdddcf6dcc81df2a8fd8b5bf90997d30cf9f" , "ciao" , 
#                      17 , 2.0 , 2.0 , 33.0 , 
#                      "mp3" , "3533fdedcf6dcc81df2a8fd8b5bf90997d30cf4f" , "peo" , "pop" )
#     db.insert_track( "3533fd5dcf6dcc81df2a8fd8b5bf90997d30cf9f" , "ciao" , 
#                      3 , 2.0 , 2.0 , 33.0 , 
#                      "mp3" , "3533fdedcf6dcc81df2a8fd8b5bf90997d30cf4f" , "meo" )
#     db.insert_track( "3533fd7dcf6dcc81df2a8fd8b5bf90997d30cf9f" , "ciao" , 
#                      5 , 2.0 , 2.0 , 33.0 , 
#                      "mp34" , "3533fdedcf6dcc81df2a8fd8b5bf90997d30cf4f" , "peo" , "pop" )
#     db.insert_track( "3533fd1dcf6dcc81df2a8fd8b5bf90997d30cf9f" , "ciao" , 
#                      17 , 2.0 , 2.0 , 33.0 , 
#                      "mp5" , "3533fdedcf6dcc81df2a8fd8b5bf90997d3t0geo" , "geo" , "rock" )
#     
#     db.insert_album( "3533fdedcf6dcc81df2a8fd8b5bf90997d30cf4f" , "pinco" , 17 )
#     db.insert_album( "3533fdedcf6dcc81df2a8fd8b5bf90997d3t0geo" , "geo" , 21 )
#     
#     print ( db._tracks )
#     print ( db._artists )
#     print ( db._codec )
#     print ( db._genre )
#     print ( db._dr )
#     print ( db._albums )
#     
#     db.commit_insert_session()
#     
#     exit()
#===============================================================================
    
    options = parse_args()

    if options.version :
        print_msg( dr14_version() )
        return

    init_log( logging.DEBUG )
    logging.disable( logging.INFO )
    
    numpy.seterr(all='ignore')
    
    #print( options )

    if options.path_name != None:
        path_name = os.path.abspath( options.path_name )
    else:
        path_name = os.path.abspath( '.' )
        
    if not( os.path.exists( path_name ) ) :
        print_msg( "Error: The input directory \"%s\" don't exixst! " % path_name )
        return 

    if options.out_dir and not( os.path.exists( options.out_dir ) ) :
        print_msg( "Error (-o): The target directory \"%s\" don't exixst! " % options.out_dir )
        return 

    if options.quiet :
        set_quiet_msg()

    l_ver = TestVer()
    l_ver.start()
    
    print_msg( path_name )
    print_msg( "" )

    if options.recursive :
        subdirlist = list_rec_dirs( path_name )
    else :
        subdirlist = [] 
        subdirlist.append( path_name )
    
          
    #print ( subdirlist )

    if run_analysis_opt( options , path_name ) :
        return 1

     
    if options.scan_file:
                
        dr = DynamicRangeMeter()
        r = dr.scan_file( path_name )
        
        if r == 1:
            print_out( "" )
            print_out( dr.res_list[0]['file_name'] + " :" )
            print_out( "DR      = %d" % dr.res_list[0]['dr14'] )
            print_out( "Peak dB = %.2f" % dr.res_list[0]['dB_peak'] )
            print_out( "Rms dB  = %.2f" % dr.res_list[0]['dB_rms'] )
            return 1 
        else:
            print_msg( "Error: invalid audio file" )
            return 0


    if options.out_dir == "" :
        out_dir = None
    else :
        out_dir = options.out_dir

    if options.append and out_dir == None:
        out_dir = path_name
    
    if options.files_list:
        (success,clock,r) = scan_files_list(options.path_name,options,out_dir)
    else:    
        (success,clock,r) = scan_dir_list(subdirlist,options,out_dir)
            
    if success :
        print_msg( "Success! " )
        print_msg( "Elapsed time: %2.2f sec" % clock )
    else:
        print_msg("No audio files found\n")
        print_msg(" Usage: %s [options] path_name \n\nfor more details type \n%s --help\n" % ( get_exe_name() , get_exe_name() ) )

    if sys.platform.startswith('linux'):
        subprocess.call( "stty sane" , shell=True ) 

    if test_new_version() :
        print_msg( "\n----------------------------------------------------------------------" )
        print_msg( " A new version of dr14_t.meter [ %s ] is available for download \n please visit: %s" % ( get_new_version() , get_home_url() ) )
        print_msg( "----------------------------------------------------------------------\n" )
    
    return r


if __name__ == '__main__':
    main()

