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
from dr14tmeter.dynamic_range_meter import *
from dr14tmeter.table import *
from dr14tmeter.dr14_global import dr14_version, TestVer, test_new_version, get_home_url, get_new_version
import subprocess
import sys
import re
    
def main():
	
	l_ver = TestVer()
	l_ver.start()

	desc = "Compute the DR14 value of the audio files according to the algorithm " 
	desc =  desc + "described by the Pleasurize Music Foundation "
	desc =  desc + "Visit: http://www.dynamicrange.de/"

	use = "usage: %prog [options] path_name"

	parser = OptionParser( description=desc ,  usage=use  , version="%prog " + dr14_version()  )

	parser.add_option("-m", "--multithread",
		action="store_true",
		dest="multithread",
		default=False,
		help="Usees the multi-Core mode")

	parser.add_option("-f", "--file",
		action="store_true",
		dest="scan_file",
		default=False,
		help="Compute the DR14 of a single file and exit")

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
		return 1 

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

	print ( path_name )

	dr = DynamicRangeMeter()

	
	if options.scan_file:
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


	a = time.time()
	if not options.multithread:
	        r = dr.scan_dir( path_name )
	else:
		cpu = multiprocessing.cpu_count() / 2
		if cpu <= 2:
			cpu = 2
		else:
			cpu = int( round( cpu ) )

		r = dr.scan_dir_mt( path_name , cpu )

	b = time.time() - a

	print( "Elapsed time: %2.2f" % b )
	
	if r == 0:
		print("No audio files found")
		return r


	if options.out_dir == "" :
		out_dir = path_name
	else :
		out_dir = options.out_dir


	out_list = "" ;
	if 'b' in options.out_tables:
		dr.fwrite_dr14( os.path.join( out_dir , "dr14_bbcode.txt" ) , BBcodeTable() )
		out_list = " dr14_bbcode.txt "
		
	if 't' in options.out_tables:
		dr.fwrite_dr14( os.path.join( out_dir , "dr14.txt" ) , TextTable() )
		out_list = out_list + " dr14.txt "
		
	if 'h' in options.out_tables:
		dr.fwrite_dr14( os.path.join( out_dir , "dr14.html" ) , HtmlTable() )
		out_list = out_list + " dr14.html "

	print( "DR = " + str( dr.dr14 ) )

	print("")
	print("- The full result has been written in the files: %s" % out_list )
	print("- located in the directory:")
	print( out_dir )
	print("")

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

