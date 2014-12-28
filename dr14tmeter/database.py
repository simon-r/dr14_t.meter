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

import sqlite3 
import threading

from dr14tmeter.dr14_config import get_db_path

unique_db_object = 0 ;

lock_db = threading.Lock()

class dr_database :
    
    def __init__(self):
        
        global unique_db_object
        global lock_db
        
        lock_db.acquire()
        if unique_db_object > 0 :
            lock_db.release()
            raise Exception("Error: database.dr_database is not unique !")
        unique_db_object = 1
        lock_db.release()
        
        self._insert_session = False
        
    
    def build_database(self):
        global lock_db
        lock_db.acquire()
        if self._insert_session :
            lock_db.release()
            raise Exception("Error: database.build_database It's impossible to build the database during an insertion !")        
        db = self.dr14_db_main_structure_v1()
        
        conn = sqlite3.connect( get_db_path() )
        c = conn.cursor()
        
        conn.execute( db )
        conn.commit()
        c.close()    
            
        self.ungrade_db()
        lock_db.release()
        
    def open_insert_session(self):
        global lock_db
        lock_db.acquire()
        
        if self._insert_session :
            lock_db.release()
            raise Exception("Error: database.open_insert_session session already opened !")
        self._insert_session = True
        
        self._tracks = {}
        self._albums = {}
        self._artists = {}
        
        lock_db.release()
    
    def commit_insert_session(self):
        global lock_db
        lock_db.acquire()
        
        self._insert_session = False
        lock_db.release()
    
    def insert_track( self , title , artist ,  dr , peak , rms , duration , codec , album_sha1 , track_sha1 ):
        global lock_db
        lock_db.acquire()
        
        lock_db.release()
        
    def insert_album( self , title , sha1 ):
        global lock_db
        lock_db.acquire()
        
        lock_db.release()
        
    def insert_artist( self , name ):
        global lock_db
        lock_db.acquire()
        
        lock_db.release()
        
    def dr14_db_main_structure_v1(self):
        db = """
        
            create table Db_Version (
                Version integer not null unique 
            ) ;
            
            insert into Db_Version ( Version ) values ( 1 ) ;
        
            create table Artist (
                Id integer primary key autoincrement ,
                Name varchar(60)
            ) ;      
        
            create table track (
                Id integer primary key autoincrement ,
                Title varchar(60) ,
                rms float ,
                peak float ,
                sha1 varchar(40) not null ,                
                IdArtist integer not null unique ,
                foreign key ( IdArtist ) references Artist( Id ) 
            ) ;
            
            create table Album (
                Id integer primary key autoincrement ,
                DR integer not null ,
                Title varchar(100) 
            ) ;           
            
            create table DR (
                Id integer primary key autoincrement ,
                DR integer not null unique 
            ) ;
            
            create table Date (
               Date integer not null unique 
            ) ;
                        
            create table Genre (
                Id integer primary key autoincrement ,
                Name varchar(40) 
            ) ;
            
            create table DR_track (
                IdDr integer not null unique ,
                IdTrack integer not null unique ,
                primary key ( IdDr , IdTrack ),
                foreign key ( IdDr ) references DR ( Id ),
                foreign key ( IdTrack ) references track ( Id )
            ) ;
            
            create table DR_Album (
                IdDr integer not null unique ,
                IdAlbum integer not null unique ,
                primary key ( IdDr , IdAlbum ),
                foreign key ( IdDr ) references DR ( Id ),
                foreign key ( IdAlbum ) references Album ( Id )
            ) ;
            
            create table Genre_track (
                IdGenre integer not null unique ,
                IdTrack integer not null unique ,
                primary key ( IdGenre , IdTrack ) ,
                foreign key ( IdGenre ) references Genre ( Id ) ,
                foreign key ( IdTrack ) references track ( Id )
            ) ;
            
            create table Date_track (
                IdDate integer not null unique ,
                IdTrack integer not null unique ,
                primary key ( IdDate , IdTrack ) ,
                foreign key ( IdDate ) references Date ( Id ) ,
                foreign key ( IdTrack ) references track ( Id )
            ) ;         
            
            create table Artist_track (
                IdArtist integer not null unique ,
                IdTrack integer not null unique ,
                primary key ( IdArtist , IdTrack ) ,
                foreign key ( IdArtist ) references Artist ( Id ) ,
                foreign key ( IdTrack ) references track ( Id )
            ) ;     
                        
            create table Album_track (
                IdAlbum integer not null unique ,
                IdTrack integer not null unique ,
                primary key ( IdAlbum , IdTrack ) ,
                foreign key ( IdAlbum ) references Album ( Id ) ,
                foreign key ( IdTrack ) references track ( Id )
            ) ;              
            
        """
        
        return db
    
    def ungrade_db(self):
        None
    
    
    