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


from numpy  import *
import math
import numpy


def dr_rms( y ) :
    n = y.shape
    return numpy.sqrt( 2.0 * numpy.sum( y**2.0 , 0 ) / float(n[0]) )

def u_rms( y ) :
    n = y.shape
    return numpy.sqrt( numpy.sum( y**2.0 , 0 ) / float(n[0]) )


def decibel_u( y , ref ) :
    return 20.0 * numpy.log10( y / ref )


def decibel_p( y , ref ) :
    return 10.0 * numpy.log10( y / ref )
    
def audio_min() :
    return 1.0/(2.0**24)

def audio_min16():
    return 1.0/(2.0**16)

def normalize( y , ml=1.0 ):
    m = numpy.max( numpy.abs( y ) )
    return ml * ( y * (1.0/m) )