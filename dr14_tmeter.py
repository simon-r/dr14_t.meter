#!/usr/bin/python3

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
    
    
from dynamic_range_meter import *
import os
from optparse import OptionParser
from time import  time
import multiprocessing

    
def main():
    
    parser = OptionParser(usage="usage: %prog [options] dir_name", version="%prog 0.5" )
    
    parser.add_option("-m", "--multithread",
                action="store_true",
                dest="multithread",
                default=False,
                help="Start the multithread mode")
    
    (options, args) = parser.parse_args()
    
    if len(args) <= 0:
        parser.error("wrong number of arguments")
        return 1 
    
    print( args )
    
    dir_name = args[0]
    
    dr = DynamicRangeMeter()
    
    cpu = multiprocessing.cpu_count()
        
    a = time()
    if not options.multithread:
        r = dr.scan_dir(dir_name)
    else:
        r = dr.scan_dir_mt(dir_name, round( cpu / 2 ) )
    b = time() - a
    
    print( "Elapsed time: " + str(b) )
    
    if r == 0:
        print("No audio files found")
        return r
    
    dr.fwrite_dr14( os.path.join( dir_name , "dr14_bbcode.txt" ) , BBcodeTable() )
    dr.fwrite_dr14( os.path.join( dir_name , "dr14.txt" ) , TextTable() )
    dr.fwrite_dr14( os.path.join( dir_name , "dr14.html" ) , HtmlTable() )
    
    print( "DR = " + str( dr.dr14 ) )

    print("end") 
    
    return r

if __name__ == '__main__':
    main()

