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

class StructDuration:
    def __init__( self ):
        self.tm_min = 0
        self.tm_sec = 0
    
    def set_samples( self , samples , Fs ) :
        mint = samples * (1.0 / Fs) / 60.0 
        self.tm_min = int( mint )
        self.tm_sec = int( ( mint - self.tm_min ) * 60.0 )
    
    def to_str( self ):
        return str( self.tm_min ) + ":%02d" % int(self.tm_sec)
    
    def to_float( self ):
        return float( self.tm_min ) + float(int(self.tm_sec))/100.0
    
    def float_to_str( self , f ):
        return "%d:%02d" % ( int(f) , int( 100*( f - int(f) ) ) )
        
