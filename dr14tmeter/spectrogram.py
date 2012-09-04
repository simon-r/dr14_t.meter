# dr14_t.meter: compute the DR14 value of the given audiofiles
# Copyright (C) 2011  Simone Riva
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import numpy
from dr14tmeter.audio_math import *

try:
    import matplotlib.pyplot as pyplot
    import matplotlib.mlab as mlab
    import pylab
except:
    ____foo = None
 
    
def spectrogram( Y , Fs ):
    
    s = Y.shape
    
    if len( Y.shape ) > 1 :
        ch = s[1]
    else :
        ch = 1
    
    #Ym = numpy.sum( Y , 1 ) / float(ch)
    
    
    for j in numpy.arange(ch):
        pyplot.subplot(210+j+1)
        pylab.specgram( Y[:,j] , NFFT=Fs , Fs=Fs , cmap='gnuplot2' )
        
        mean_x = numpy.array([ 0 , s[0]*(1/Fs) ])
        mean_x = numpy.array([ mean , mean ])
        
        pyplot.axis([ 0, s[0]*(1/Fs), 0, Fs / 2.0 ])
    
        pyplot.title( "Channel %d" % j )
        pyplot.xlabel('Time [sec]')
        pyplot.ylabel('Freq. [Hz]')
        pyplot.grid(True)
        
        pyplot.title( "Channel: %d"%int(j+1))
     
    pyplot.show()