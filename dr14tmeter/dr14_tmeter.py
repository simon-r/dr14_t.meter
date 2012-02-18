#!/usr/bin/python

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
from dr14tmeter.functions_main import *

    
def main():
    
    (options, args) = parse_args()

 

    #print( args )

    path_name = os.path.abspath( args[0] )

    if not( os.path.exists( path_name ) ) :
        print( "Error: The input directory \"%s\" don't exixst! " % path_name )
        return 

    if options.out_dir != "" and not( os.path.exists( options.out_dir ) ) :
        print( "Error (-o): The target directory \"%s\" don't exixst! " % options.out_dir )
        return 

    if re.search( ".*[^htb].*" , options.out_tables ) :
        print( "Error (-t) : Invalid table code" )
        return 

    l_ver = TestVer()
    l_ver.start()
    
    print ( path_name )
    print( "" )

    if options.recursive :
        subdirlist = list_rec_dirs( path_name )
    else :
        subdirlist = [] 
        subdirlist.append( path_name )
        
    #print ( subdirlist )
        
    if options.scan_file:
        dr = DynamicRangeMeter()
        r = dr.scan_file( path_name )
        
        if r == 1:
            print( "" )
            print( dr.res_list[0]['file_name'] + " :" )
            print( "DR      = %d" % dr.res_list[0]['dr14'] )
            print( "Peak dB = %.2f" % dr.res_list[0]['dB_peak'] )
            print( "Rms dB  = %.2f" % dr.res_list[0]['dB_rms'] )
            return 1 
        else:
            print ( "Error: invalid audio file" )
            return 0


    if options.out_dir == "" :
        out_dir = None
    else :
        out_dir = options.out_dir


    a = time.time()


    for cur_dir in subdirlist :
        dr = DynamicRangeMeter()
        print ( "\n------------------------------------------------------------ " )		        
        print ( "> Scan Dir: %s \n" % cur_dir )
        
        if not options.multithread:
            r = dr.scan_dir( cur_dir )
        else:
            cpu = multiprocessing.cpu_count() / 2
            if cpu <= 2:
                cpu = 2
            else:
                cpu = int( round( cpu ) )
                
            r = dr.scan_dir_mt( cur_dir , cpu )
            
        if r == 0:
            print("No audio files found\n")
            continue
        
        write_results( dr , options , out_dir , cur_dir )        
         
    
    b = time.time() - a
    print( "Elapsed time: %2.2f" % b )
    
    print("Success! ") 

    if sys.platform.startswith('linux'):
        subprocess.call( "stty sane" , shell=True ) 

    if test_new_version() :
        print( "\n----------------------------------------------------------------------" )
        print( " A new version of dr14_t.meter [ %s ] is available for download \n please visit: %s" % ( get_new_version() , get_home_url() ) )
        print( "----------------------------------------------------------------------\n" )
    
    return r

if __name__ == '__main__':
    main()

