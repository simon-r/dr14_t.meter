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


class ComputeDr :
    def __init__(self):
        self.duration = [] ;
        self.Dr_lr = (0,0)
    
    def compute( self , Y , Fs ):
        pass
    
    def get_duration( self ) :
        return self.duration
    
    def get_dr_lr( self ) :
        return self.Dr_lr
    

class ComputeDR14( ComputeDr ) :
    def compute( self , Y , Fs ):
       return compute_dr14(  Y , Fs , self.duration , self.Dr_lr )
       

class ComputeDRV( ComputeDr ) :
    def compute( self , Y , Fs ):
       return compute_dr14(  Y , Fs , self.duration , self.Dr_lr )