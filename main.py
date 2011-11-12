import compute_dr14
import read_wav


def main():
	
	(Y , fs ) = read_wav.read_wav( "p.wav" )
	(dr14 , p , rms ) = compute_dr14.compute_dr14( Y , fs ) 
	
	print( dr14 ) 
	
	print("ciao") 
	
	return 0

if __name__ == '__main__':
	main()

