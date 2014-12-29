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

        self._tracks = {}
        self._albums = {}
        self._artists = {}
        self._genre = {}
        self._codec = {} 
        self._dr = {}
        
        self._id_artist = 0
        self._id_album = 0
        self._id_track = 0
        self._id_genre = 0
        self._id_codec = 0
        self._id_dr = 0
        
    
    def build_database(self):
        global lock_db
        lock_db.acquire()
        if self._insert_session :
            lock_db.release()
            raise Exception("Error: database.build_database It's impossible to build the database during an insertion !")        
        db = self.dr14_db_main_structure_v1()
        
        conn = sqlite3.connect( get_db_path() )
        
        conn.executescript( db )
        conn.commit()
            
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
        self._genre = {}
        self._codec = {}
        self._dr = {}        
        
        self._id_artist = self.query( "select max(Id) from Artist" ).pop()[0]
        self._id_artist = 0 if self._id_artist == None else self._id_artist + 1
        
        self._id_album = self.query( "select max(Id) from Album" ).pop()[0]
        self._id_album = 0 if self._id_album == None else self._id_album + 1
        
        self._id_track = self.query( "select max(Id) from track" ).pop()[0]
        self._id_track = 0 if self._id_track == None else self._id_track + 1
        
        self._id_genre = self.query( "select max(Id) from Genre" ).pop()[0]
        self._id_genre = 0 if self._id_genre == None else self._id_genre + 1
        
        self._id_codec = self.query( "select max(Id) from Codec" ).pop()[0]
        self._id_codec = 0 if self._id_codec == None else self._id_codec + 1
        
        self._id_dr = self.query( "select max(Id) from DR" ).pop()[0]
        self._id_dr = 0 if self._id_dr == None else self._id_dr + 1
        
        lock_db.release()
    
    def commit_insert_session(self):
        global lock_db
        lock_db.acquire()
        if self._insert_session == False :
            lock_db.release()
            raise Exception("Error: database.commit_insert_session the session has not been opened !")
        
        self._insert_session = False
        lock_db.release()
    
    def insert_track( self , track_sha1 , title , dr , rms , peak , duration , codec , album_sha1="" , artist="" , genre=None ):
        global lock_db
        lock_db.acquire()
        if self._insert_session == False :
            lock_db.release()
            raise Exception("Error: database.insert_track the insert session has not been opened !")
        
        q = "select Id from track where sha1 = \"%s\" " % track_sha1
        rq = self.query( q )
        
        if len( rq ) > 0 :
            lock_db.release()
            return rq.pop()[0]
        
        q = "select Id from artist where name = \"%s\" " % artist
        rq = self.query( q )
        if len( rq ) == 0 and not ( artist in self._artists.values() ) :
            artist_id = self.__insert_artist( artist )
        elif len( rq ) > 0 :
            artist_id = rq.pop()[0]
        else :
            artist_id = [k for (k, v) in self._artists.items() if v == artist][0]
            
        q = "select Id from codec where name = \"%s\" " % codec
        rq = self.query( q )
        if len( rq ) == 0 and not ( artist in self._codec.values() ) :
            codec_id = self.__insert_codec( codec )
        elif len( rq ) > 0 :
            codec_id = rq.pop()[0]
        else :
            codec_id = [k for (k, v) in self._codec.items() if v == codec][0]            
         
        genre_id = -1   
        if genre != None : 
            q = "select Id from Genre where name = \"%s\" " % genre
            rq = self.query( q )
            if len( rq ) == 0 and not ( genre in self._genre.values() ) :
                genre_id = self.__insert_genre( genre )
            elif len( rq ) > 0 :
                genre_id = rq.pop()[0]
            else :
                genre_id = [k for (k, v) in self._genre.items() if v == genre][0] 
                
        q = "select Id from DR where DR = %d " % dr 
        rq = self.query( q )
        if len( rq ) == 0 and not ( dr in self._dr.values() ) :
            dr_id = self.__insert_dr( dr )
        elif len( rq ) > 0 :
            dr_id = rq.pop()[0]
        else :
            dr_id = [k for (k, v) in self._dr.items() if v == dr][0]   
        
            
        self._tracks[track_sha1] = [ self._id_track , title , dr_id , peak , rms , duration , codec_id , album_sha1 , artist_id , genre_id ]
        self._id_track = self._id_track + 1
        
        lock_db.release()
        
        return self._id_track - 1
    
        
    def insert_album( self , album_sha1 , title , dr ):
        global lock_db
        lock_db.acquire()
        
        q = "select Id from Album where sha1 = \"%s\" " % album_sha1 
        rq = self.query( q )
        
        if len( rq ) > 0 :
            lock_db.release()
            return rq.pop()[0]

        q = "select Id from DR where DR = %d " % dr 
        rq = self.query( q )
        if len( rq ) == 0 and not ( dr in self._dr.values() ) :
            dr_id = self.__insert_dr( dr )
        elif len( rq ) > 0 :
            dr_id = rq.pop()[0]
        else :
            dr_id = [k for (k, v) in self._dr.items() if v == dr][0] 
        
        self._albums[album_sha1] = [ self._id_album , title , dr_id ]
        self._id_album = self._id_album + 1
        
        lock_db.release()
        
        return self._id_album - 1
        
    def __insert_artist( self , name ):
        
        self._artists[self._id_artist] = name
        self._id_artist = self._id_artist + 1
                
        return self._id_artist - 1
        
    def __insert_codec( self , codec ):
        
        self._codec[self._id_codec] = codec
        self._id_codec = self._id_codec + 1
                
        return self._id_codec - 1
    
    def __insert_genre( self , genre ):
        
        self._genre[self._id_genre] = genre
        self._id_genre = self._id_genre + 1
                
        return self._id_genre - 1
    
    def __insert_dr( self , dr ):
        
        self._dr[self._id_dr] = dr
        self._id_dr = self._id_dr + 1
                
        return self._id_dr - 1   
        
        
    def query( self , query ):
        conn = sqlite3.connect( get_db_path() )
        c = conn.cursor()
        
        c.execute( query )
        res_l = c.fetchall()
        c.close()
        
        return res_l
             
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
                    
            create table Track (
                Id integer primary key autoincrement ,
                Title varchar(60) ,
                rms float ,
                peak float ,
                duration float ,
                sha1 varchar(40) not null ,                
                IdArtist integer not null unique ,
                foreign key ( IdArtist ) references Artist( Id ) 
            ) ;
            
            create table Album (
                Id integer primary key autoincrement ,
                sha1 varchar(40) not null ,
                Title varchar(100) 
            ) ;           
            
            create table DR (
                Id integer primary key autoincrement ,
                DR integer not null unique 
            ) ;
            
            create table Date (
               Date integer not null unique 
            ) ;
            
            create table Codec (
                Id integer primary key autoincrement ,
                Name varchar[15] 
            ) ;
            
            insert into Codec ( Name ) values ( "wav" ) ;
            insert into Codec ( Name ) values ( "mp3" ) ;
            insert into Codec ( Name ) values ( "flac" ) ;
            insert into Codec ( Name ) values ( "mp4" ) ;
            insert into Codec ( Name ) values ( "ogg" ) ;
            insert into Codec ( Name ) values ( "ac3" ) ;
            insert into Codec ( Name ) values ( "wma" ) ;
            insert into Codec ( Name ) values ( "ape" ) ;
                        
            create table Genre (
                Id integer primary key autoincrement ,
                Name varchar(40) 
            ) ;
            
            create table DR_Track (
                IdDr integer not null unique ,
                IdTrack integer not null unique ,
                primary key ( IdDr , IdTrack ),
                foreign key ( IdDr ) references DR ( Id ),
                foreign key ( IdTrack ) references Track ( Id )
            ) ;
            
            create table Codec_Track (
                IdCodec integer not null unique ,
                IdTrack integer not null unique ,
                primary key ( IdCodec , IdTrack ),
                foreign key ( IdCodec ) references Codec ( Id ),
                foreign key ( IdTrack ) references Track ( Id )
            ) ;            
            
            create table DR_Album (
                IdDr integer not null unique ,
                IdAlbum integer not null unique ,
                primary key ( IdDr , IdAlbum ),
                foreign key ( IdDr ) references DR ( Id ),
                foreign key ( IdAlbum ) references Album ( Id )
            ) ;
            
            create table Genre_Track (
                IdGenre integer not null unique ,
                IdTrack integer not null unique ,
                primary key ( IdGenre , IdTrack ) ,
                foreign key ( IdGenre ) references Genre ( Id ) ,
                foreign key ( IdTrack ) references Track ( Id )
            ) ;
            
            create table Date_Track (
                IdDate integer not null unique ,
                IdTrack integer not null unique ,
                primary key ( IdDate , IdTrack ) ,
                foreign key ( IdDate ) references Date ( Id ) ,
                foreign key ( IdTrack ) references Track ( Id )
            ) ;         
            
            create table Artist_Track (
                IdArtist integer not null unique ,
                IdTrack integer not null unique ,
                primary key ( IdArtist , IdTrack ) ,
                foreign key ( IdArtist ) references Artist ( Id ) ,
                foreign key ( IdTrack ) references Track ( Id )
            ) ;     
                        
            create table Album_Track (
                IdAlbum integer not null unique ,
                IdTrack integer not null unique ,
                primary key ( IdAlbum , IdTrack ) ,
                foreign key ( IdAlbum ) references Album ( Id ) ,
                foreign key ( IdTrack ) references Track ( Id )
            ) ;
            
        """
        
        return db
    
    def ungrade_db(self):
        None
    
    
    