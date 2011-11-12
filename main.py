import compute_dr14
import read_wav


def main():
	
	(Y , fs, ch ) = read_wav.read_wav( "01.wav" )
	(dr14 , p , rms ) = compute_dr14.compute_dr14( Y , fs ) 
	
	print( "dr14:" , dr14 ) 
	print( "peak;" , p ) 
	print( "rms:" , rms ) 
	
	print("end") 
	
	return 0

if __name__ == '__main__':
	main()

