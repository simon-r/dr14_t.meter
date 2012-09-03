# dr14_t.meter: compute the DR14 value of the given audiofiles
# Copyright (C) 2011 - 2012  Simone Riva
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
except:
    ____foo = None
    

def compute_lev_hist ( Y , Fs , duration=None , bins=100 , plot=True , title=None ):
    
    s = Y.shape
    
    if len( Y.shape ) > 1 :
        ch = s[1]
    else :
        ch = 1
    
    Ym = numpy.sum( Y , 1 ) / float(ch)

    if plot :
        ( hist , bin_edges , patches ) = pyplot.hist(  Ym  , 100 , normed=True  )
        
        pyplot.grid(True)
        
        if title != None:
            hist_title = title
        else:
            hist_title = "Hystogram of levels"
        
        pyplot.title(r'%s'%hist_title)
        
        pyplot.show()
    else:
        ( hist , bin_edges ) = numpy.histogram( rms , bins=bins , normed=True )
        
    return ( hist , bin_edges )