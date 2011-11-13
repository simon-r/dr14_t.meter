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
	
	print("end") 
	
	return 0

if __name__ == '__main__':
	main()

