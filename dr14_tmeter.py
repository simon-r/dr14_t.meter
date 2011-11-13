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


import compute_dr14
import read_wav
from dynamic_range_meter import *
import os
from optparse import OptionParser


def main():
	
	parser = OptionParser(usage="usage: %prog [options] dir_name", version="%prog 0.5" )
	
	(options, args) = parser.parse_args()
	
	if len(args) != 1:
		parser.error("wrong number of arguments")
		return 1 
	
	print( args )
	
	dir_name = args[0]
	
	dr = DynamicRangeMeter()
	dr.scan_dir(dir_name)
	
	dr.fwrite_dr14( os.path.join( dir_name , "dr14_bbcode.txt" ) , BBcodeTable() )
	
	print( "DR = " + str( dr.dr14 ) )
	
	print("end") 
	
	return 0

if __name__ == '__main__':
	main()

