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
import os
import logging

message_file = sys.stderr
out_file = sys.stdout
err_file = sys.stderr
mode = "verbose"


logger = logging.getLogger('dr14log')





def init_log( lev=logging.DEBUG ):
    global logger
        
    logger = logging.getLogger('dr14log')
    logger.setLevel( logging.DEBUG )
    stream_h = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    stream_h.setLevel( lev )
    stream_h.setFormatter( formatter )
    
    logger.addHandler( stream_h )
    logger.debug("ciao")

def dr14_log_debug( message ):
    global logger    
    logger.debug( message )

def dr14_log_info( message ):
    global logger    
    logger.info( message )

########

def print_msg( string ) :
    global message_file
    message_file.write( "%s\n" % string )
   
def print_err( string ):
    global err_file
    err_file.write( "Error: %s \n" % string )
    
def print_out( string ) :
    global out_file
    out_file.write( "%s\n" % string )

    
def set_verbose_msg() :
    global message_file
    global mode
    
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