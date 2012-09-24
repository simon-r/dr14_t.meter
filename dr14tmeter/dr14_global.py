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
import re
import threading

from dr14tmeter.out_messages import print_msg


###########################
# Current version
v_major    = 1
v_minor    = 0
v_revision = 10
###########################

# latest version
l_major = 0
l_minor = 0
l_revision = 0

lock_ver = threading.Lock()


def dr14_version():
    global v_major
    global v_minor
    global v_revision
    return "%d.%d.%d" % ( v_major , v_minor , v_revision )

def min_dr() :
    return -10000

def get_exe_name():
    return "dr14_tmeter"

class TestVer(threading.Thread):
    def run(self):
        _dr14_get_latest_version()



def _dr14_get_latest_version():
    
    global l_major
    global l_minor
    global l_revision
    global lock_ver
    
    ver_url = "http://simon-r.github.com/dr14_t.meter/ver.html"
    #print_msg ( ver_url )
    
    try:
        if sys.version_info[0] > 2 :
            import urllib.request
            opener = urllib.request.FancyURLopener({})
            f = opener.open( ver_url )
            vr = f.read()
            vr = vr.decode()
        else :
            import urllib
            opener = urllib.FancyURLopener({})
            f = opener.open( ver_url )
            vr = f.read()
    except:
        return 
    
    re_flags = ( re.MULTILINE | re.IGNORECASE | re.UNICODE )
    m = re.search( r"<div\s+id=\"version\">\s*(\d+)\.(\d+)\.(\d+)\s*</div>" , vr , re_flags )
    
    if m == None:
        return 
    
    
    lock_ver.acquire()
    if len( m.groups() ) == 3 :
        l_major = int( m.groups()[0] )
        l_minor = int( m.groups()[1] )
        l_revision = int( m.groups()[2] )
    else :
        l_major = 0
        l_minor = 0
        l_revision = 0
        
    lock_ver.release()
    

    
def test_new_version():
    global l_major
    global l_minor
    global l_revision
    
    global v_major
    global v_minor
    global v_revision
    
    lock_ver.acquire()
    
    curr_ver = ( v_major , v_minor , v_revision )
    online_ver = ( l_major , l_minor , l_revision )
    
    for i in range( 0 , 3 ) :
        if online_ver[i] > curr_ver[i] :
            lock_ver.release()
            return True
        elif online_ver[i] < curr_ver[i] :
            lock_ver.release()
            return False
    
    lock_ver.release()
    return False
    

def get_new_version():
    
    global lock_ver
    
    lock_ver.acquire()
    res = "%d.%d.%d" % ( l_major , l_minor , l_revision )
    lock_ver.release()
    
    return res
    

def get_home_url():
    return "http://simon-r.github.com/dr14_t.meter"
        
      
      
def test_matplotlib_modules( fun_name ):
    try:
        import matplotlib
    except ImportError:
        print_msg( "The %s function require the installation of MatPlotLib: http://matplotlib.sourceforge.net" % fun_name )
        return False
    
    return True


def test_hist_modules():
    try:
        import matplotlib
    except ImportError:
        print_msg( "The histogram function require the installation of MatPlotLib: http://matplotlib.sourceforge.net" )
        return False
    
    return True

def test_compress_modules():
    try:
        import scipy
    except:
        print_msg( "The compression function require the installation of SciPy: http://www.scipy.org/" )
        return False
    
    return True
        
