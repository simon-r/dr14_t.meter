import compute_dr14
import read_wav
from dynamic_range_meter import *
import os

def main():
	
	dir_name = '.'
	
	dr = DynamicRangeMeter()
	dr.scan_dir(dir_name)
	
	dr.fwrite_dr14( os.path.join( dir_name , "dr14_bbcode.txt" ) , BBcodeTable() )
	
	print("end") 
	
	return 0

if __name__ == '__main__':
	main()

