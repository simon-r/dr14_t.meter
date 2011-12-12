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
from time import  time
import multiprocessing
from dr14tmeter.dynamic_range_meter import *
from dr14tmeter.table import *

    
def main():

	desc = "Compute the DR14 value of the audio files according to the algorithm " 
	desc =  desc + "described by the Pleasurize Music Foundation "
	desc =  desc + "Visit: http://www.dynamicrange.de/"

	use = "usage: %prog [options] path_name"

	parser = OptionParser( description=desc ,  usage=use  , version="%prog 0.5.4"  )

	parser.add_option("-m", "--multithread",
		action="store_true",
		dest="multithread",
		default=False,
		help="Start the multithread mode")

	parser.add_option("-f", "--file",
		action="store_true",
		dest="scan_file",
		default=False,
		help="Compute the DR14 of a single file")

	(options, args) = parser.parse_args()

	if len(args) <= 0:
		parser.error("wrong number of arguments")
		return 1 

	#print( args )

	path_name = os.path.abspath( args[0] )

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


	a = time()
	if not options.multithread:
	        r = dr.scan_dir( path_name )
	else:
		cpu = multiprocessing.cpu_count() / 2
		if cpu <= 2:
			cpu = 2
		else:
			cpu = int( round( cpu ) )

		r = dr.scan_dir_mt( path_name , cpu )

	b = time() - a

	print( "Elapsed time: " + str(b) )
	
	if r == 0:
		print("No audio files found")
		return r

	dr.fwrite_dr14( os.path.join( path_name , "dr14_bbcode.txt" ) , BBcodeTable() )
	dr.fwrite_dr14( os.path.join( path_name , "dr14.txt" ) , TextTable() )
	dr.fwrite_dr14( os.path.join( path_name , "dr14.html" ) , HtmlTable() )

	print( "DR = " + str( dr.dr14 ) )

	print("")
	print("- The full result has been written in the files: dr14_bbcode.txt, dr14.txt, dr14.html")
	print("- located in the directory:")
	print( path_name )
	print("")

	print("Success! ") 

	return r

if __name__ == '__main__':
	main()

