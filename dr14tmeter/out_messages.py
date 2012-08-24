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

import sys

message_file = sys.stderr
out_file = sys.stdout

mode = "verbose"

def print_msg( string ) :
    global message_file 
    print( string , file=message_file )
    
def print_out( string ) :
    global out_file
    print( string , file=out_file )

    
def set_verbose_msg() :
    global message_file
    
    if mode == "verbose" :
        return 
    
    close( message_file )
    
    message_file = sys.stderr

    
def set_quiet_msg() :
    global message_file
    global mode
    
    if mode == "quiet" :
        return 
    
    message_file = open(os.devnull,"w")