import sys
import re
import threading

###########################
# Current version
v_major    = 0
v_minor    = 7
v_revision = 0
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




class TestVer(threading.Thread):
    def run(self):
        _dr14_get_latest_version()



def _dr14_get_latest_version():
    
    global l_major
    global l_minor
    global l_revision
    global lock_ver
    
    ver_url = "http://simon-r.github.com/dr14_t.meter/ver.txt"
    
    try:
        if sys.version_info[0] > 2 :
            import urllib.request
            opener = urllib.request.FancyURLopener({})
            f = opener.open(ver_url)
            vr = f.read()
            vr = vr.decode()
        else :
            import urllib
            opener = urllib.FancyURLopener({})
            f = opener.open(ver_url)
            vr = f.read()
    except:
        return 
        
    m = re.match( r"(\d)\.(\d)\.(\d)" , vr )
    
    lock_ver.acquire()
    l_major = int( m.groups()[0] )
    l_minor = int( m.groups()[1] )
    l_revision = int( m.groups()[2] )
    lock_ver.release() 
    #print( "%d.%d.%d" % ( l_major , l_minor , l_revision ) )

    
def test_new_version():
    global l_major
    global l_minor
    global l_revision
    
    global v_major
    global v_minor
    global v_revision
    
    lock_ver.acquire()
    if l_major > v_major or l_minor > v_minor or l_revision > v_revision :
        lock_ver.release() 
        return True
    else:
        lock_ver.release() 
        return False
    

def get_new_version():
    
    lock_ver.acquire()
    res = "%d.%d.%d" % ( l_major , l_minor , l_revision )
    lock_ver.release()
    
    return res
    

def get_home_url():
    return "http://simon-r.github.com/dr14_t.meter"
        