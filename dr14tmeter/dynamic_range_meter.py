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

import os
import threading
import sys
import codecs
import tempfile

from dr14tmeter.compute_dr14 import compute_dr14
from dr14tmeter.compute_drv import compute_DRV
from dr14tmeter.compute_dr import *
from dr14tmeter.audio_track import *
from dr14tmeter.table import *
from dr14tmeter.dr_histogram import *
from dr14tmeter.lev_histogram import *
from dr14tmeter.compressor import DynCompressor
from dr14tmeter.wav_write import wav_write
from dr14tmeter.read_metadata import RetirveMetadata
from dr14tmeter.audio_decoder import AudioDecoder
from dr14tmeter.duration import StructDuration
from dr14tmeter.write_dr import WriteDr, WriteDrExtended

import dr14tmeter.dr14_global as dr14

from dr14tmeter.out_messages import print_msg, print_out

        

class DynamicRangeMeter:   
    
    def __init__( self ):
        self.res_list = []
        self.dir_name = '' 
        self.dr14 = 0 
        self.meta_data = RetirveMetadata()
        self.histogram = False
        self.compress = False
        
        self.compute_dr = ComputeDR14()
    
    def scan_file( self , file_name):
        
        at = AudioTrack() 
        
        duration = StructDuration() 
        
        if self.histogram :
            compute_fun = self.__compute_histogram
        elif self.compress :
            compute_fun = self.__compress
        else:
            compute_fun = self.__compute_and_append
        
        if at.open( file_name ):
            compute_fun( at , file_name )
            return 1
        else:
            return 0
        
    def scan_dir( self , dir_name ):
        
        if not os.path.isdir(dir_name) :
            return 0
        
        dir_list = sorted( os.listdir( dir_name ) )
        
        self.dir_name = dir_name 
        self.dr14 = 0 
        
        duration = StructDuration() 
        
        at = AudioTrack() 
        for file_name in dir_list:
            full_file = os.path.join( dir_name , file_name )
            
            #print_msg( full_file )
            if at.open( full_file ):
                self.__compute_and_append( at , file_name )

        self.meta_data.scan_dir( dir_name )
        if len( self.res_list ) > 0:
            self.dr14 = int( round( self.dr14 / len( self.res_list ) ) )
            return len( self.res_list )
        else:
            return 0
 

    def __compute_and_append( self , at , file_name ):
        
        duration = StructDuration()
        
        #( dr14, dB_peak, dB_rms ) = self.compute_dr.compute( at.Y , at.Fs )
        ( dr14, dB_peak, dB_rms ) = compute_dr14( at.Y , at.Fs , duration )
        
        self.dr14 = self.dr14 + dr14
        
        res = { 'file_name': file_name , 'dr14': dr14 , 'dB_peak': dB_peak , 'dB_rms': dB_rms , 'duration':duration.to_str() }
        self.res_list.append(res)
        
        print_msg( file_name + ": \t DR " + str( int(dr14) ) )
  
    
    def __compute_histogram( self , at , file_name ):
        
        duration = StructDuration()
        
        self.meta_data.scan_file( file_name )
        
        (foo,fn) = os.path.split( file_name )
        title = self.meta_data.get_value( fn , "title" )
        
        print_msg( title )
        
        compute_hist( at.Y , at.Fs , duration , title=title ) 
    
    def __compress( self , at , file_name ):
        
        (head, file_n) = os.path.split( file_name )
        
        comp = DynCompressor()
        
        full_file = os.path.join( tempfile.gettempdir() , "%s%s.wav" % ( file_n , "-compressed-" ) )
        
        cY = comp.dyn_compressor( at.Y , at.Fs )
        wav_write( full_file , at.Fs , cY )
        
        print_msg( "The resulting compressed audiotrack has been written in: %s " % full_file )
        
    
    def scan_mt( self , dir_name="" , thread_cnt=2 , files_list=[] ):
        
        self.dr14 = 0
        
        if files_list == [] :
            if not os.path.isdir(dir_name) :
                return 0
            dir_list = sorted( os.listdir( dir_name ) )
            self.dir_name = dir_name
            files_list = None
        else:
            dir_list = sorted( files_list )
            
        ad = AudioDecoder()
        
        jobs = []
        for file_name in dir_list:
            ( fn , ext ) = os.path.splitext( file_name )
            if ext in ad.formats:
                jobs.append( file_name )
        
        empty_res = { 'file_name': '' , 'dr14': dr14.min_dr() , 'dB_peak': -100 , 'dB_rms': -100 , 'duration':"0:0" }
        self.res_list = [empty_res for i in range( len(jobs) )]
        
        lock_j = threading.Lock()
        lock_res_list = threading.Lock()
        
        threads = [1 for i in range(thread_cnt)]
        job_free = [0]
        
        for t in range( thread_cnt ):
            threads[t] = ScanDirMt( dir_name, jobs , job_free , lock_j , self.res_list , lock_res_list )
            
        for t in range( thread_cnt ):
            threads[t].start() 
        
        for t in range( thread_cnt ):
            threads[t].join()
            
        succ = 0 
        for d in self.res_list:
            if d['dr14'] > dr14.min_dr():
                self.dr14 = self.dr14 + d['dr14']
                succ = succ + 1 
            
         
        #print_msg( str(self.res_list ) )
        self.meta_data.scan_dir( dir_name , files_list )
        if len( self.res_list ) > 0 and succ > 0 :
            self.dr14 = int( round( self.dr14 / succ ) )
            return succ
        else:
            return 0
        

    def fwrite_dr( self , file_name , tm , ext_table=False , std_out=False , append=False , dr_database=True ):
        
        if ext_table :
            wr = WriteDrExtended()
        else :
            wr = WriteDr()
        
        wr.set_dr_database( dr_database )
        
        self.table_txt = wr.write_dr( self , tm )        
        
        if std_out:
            print_out( self.table_txt )
            return 
        
        if append :
            file_mode = "a"
        else :
            file_mode = "w"
        
        try:
            out_file = codecs.open( file_name , file_mode , "utf-8-sig" )
        except:
            print_msg ( "File opening error [%s] :" % file_name , sys.exc_info()[0] )
            return False
        
        out_file.write( self.table_txt )
        out_file.close()
        return True
    

class ScanDirMt(threading.Thread):
    def __init__( self ,dir_name , jobs , job_free , lock_j , res_list , lock_res_list ):
        threading.Thread.__init__(self)
        self.dir_name = dir_name
        self.jobs = jobs
        self.jobs_free = job_free
        self.lock_j = lock_j
        self.res_list = res_list
        self.lock_res_list = lock_res_list
        
    def run(self):
       
        at = AudioTrack() 
        duration = StructDuration()
        
        #print_msg("start .... ")
        
        while True:
            
            #Aquire the next free job
            self.lock_j.acquire()
            
            if self.jobs_free[0] >= len(self.jobs):
                self.lock_j.release()
                return
            
            curr_job =  self.jobs_free[0]
            file_name = self.jobs[curr_job]
            self.jobs_free[0] = self.jobs_free[0] + 1
            
            self.lock_j.release()
            
            full_file = os.path.join( self.dir_name , file_name ) 
            
            if at.open( full_file ):
                ( dr14, dB_peak, dB_rms ) = compute_dr14( at.Y , at.Fs , duration )
                self.lock_res_list.acquire()
                print_msg( file_name + ": \t DR " + str( int(dr14) ) )
                self.res_list[curr_job] = { 'file_name': file_name , 'dr14': dr14 , 'dB_peak': dB_peak , 'dB_rms': dB_rms , 'duration':duration.to_str() }
                self.lock_res_list.release()
            else:
                print_msg( "- fail - " + full_file )
   
   