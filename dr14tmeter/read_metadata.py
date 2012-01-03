import subprocess
import sys


# Test example !!!!!
cmd = ["ffmpeg" , "-i" , "/media/esterno_xfs/data/Musica/Musica/aavv/01-blitzkrieg_bop_160_lame_abr.mp3" ]

#cmd = [ "ls" , "-al" ]

process = subprocess.Popen( cmd , stdout=subprocess.PIPE, stderr=subprocess.PIPE )

while True:
    out = process.stderr.readline()
    if out == '' and process.poll() != None:
        break
    if out != '':
        #sys.stdout.write(out)
        print ( ">> " + out )
        sys.stdout.flush()