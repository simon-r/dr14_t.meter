import subprocess
import sys


# Test example !!!!!
a = subprocess.check_output( [ "ffprobe" , "-show_format" , "/media/esterno_xfs/data/Musica/Musica/aavv/01-blitzkrieg_bop_160_lame_abr.mp3" ] , stderr=subprocess.STDOUT , shell=False )

print( a )

