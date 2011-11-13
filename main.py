import compute_dr14
import read_wav
from dynamic_range_meter import DynamicRangeMeter


def main():
	
	dr = DynamicRangeMeter()
	dr.scan_dir('.')
	
	
	
	print("end") 
	
	return 0

if __name__ == '__main__':
	main()

