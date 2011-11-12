import numpy
import scipy.io.wavfile

def read_wav( file_name )

	convert_8_bit = float(2**15)
	convert_16_bit = float(2**15)
	convert_32_bit = float(2**31)
	
	sample_rate, samples = scipy.io.wavfile.read(file_name)
	
	# scale to -1.0 -- 1.0
	
	if samples.stype == 'int16':
		samples = samples / (convert_16_bit + 1.0)
	elif samples.stype == 'int32':
		samples = samples / (convert_16_bit + 1.0)
	else :
		samples = samples / (convert_8_bit + 1.0)
		
	s = samples.shape
	
	if len(s) == 1:
		channels = 1 
	else:
		channels = s[1]
		
	return ( samples , channels )
	
