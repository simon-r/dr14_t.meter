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

import scipy.io.wavfile

def read_wav( file_name ):

	convert_8_bit = float(2**15)
	convert_16_bit = float(2**15)
	convert_32_bit = float(2**31)
	
	sample_rate, samples = scipy.io.wavfile.read(file_name)
	
	if samples.dtype == 'int16':
		samples = samples / (convert_16_bit + 1.0)
	elif samples.dtype == 'int32':
		samples = samples / (convert_32_bit + 1.0)
	else :
		samples = samples / (convert_8_bit + 1.0)
		
	s = samples.shape
	
	if len(s) == 1:
		channels = 1 
	else:
		channels = s[1]
		
	return ( samples , sample_rate , channels )
	
