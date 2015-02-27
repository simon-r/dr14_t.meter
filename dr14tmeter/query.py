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

from dr14tmeter.database import dr_database_singletone

def my_dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


class query :
    def __init__(self):
        self.limit = 30 
        self.keys = [] 
    
    def get_limit(self):
        return self.limit 
    
    def set_limit( self , limit ):
        self.limit = limit 
        
    limit = property( get_limit , set_limit )
    
    def get_query(self):
        NotImplementedError( "%s : is virutal and must be overridden." % sys._getframe().f_code.co_name )
        
    query = property( get_query )
    
    def exec_query(self):
        db = dr_database_singletone() ;
        return db.query( self.query , (self.limit,) , dict_factory_arg=my_dict_factory )
    
    def get_col_keys(self):
        return self.keys
        

class query_top_dr( query ):
    def __init__(self):
        super( query_top_dr , self ).__init__()
        self.keys = [ "dr" , "title" , "id" ]
        
    def get_query(self):
        q = """
        select track.id as id , track.title as title , dr.dr as dr 
           from track inner join DR_Track on DR_Track.idtrack = track.id 
                  inner join dr on dr.id = DR_Track.iddr 
                  order by dr desc
                  limit ? ;
        """
        
        return q 


class query_top_albums_dr( query ):
    def __init__(self):
        super( query_top_dr , self ).__init__()
        self.keys = [ "dr" , "album_title" , "id" ]
        
    def get_query(self):
        q = """
        select track.id as id , track.title as title , dr.dr as dr 
           from track inner join DR_Track on DR_Track.idtrack = track.id 
                  inner join dr on dr.id = DR_Track.iddr 
                  order by dr desc
                  limit ? ;
        """
        
        return q 


class query_worst_albums_dr( query ):
    def __init__(self):
        super( query_top_dr , self ).__init__()
        self.keys = [ "dr" , "album_title" , "id" ]
        
    def get_query(self):
        q = """
        select album.title as album_title , dr.dr as dr , album.id as id 
           from album inner join DR_Album on DR_Album.idalbum = album.id 
                  inner join dr on dr.id = DR_Album.iddr 
                  order by dr asc
                  limit ? ;
        """
        
        return q 
    
    
class query_worst_dr( query ):
    def __init__(self):
        super( query_top_dr , self ).__init__()
        self.keys = [ "dr" , "title" , "id" ]
        
    def get_query(self):
        q = """
        select track.id as id , track.title as title , dr.dr as dr 
           from track inner join DR_Track on DR_Track.idtrack = track.id 
                  inner join dr on dr.id = DR_Track.iddr 
                  order by dr asc
                  limit ? ;
        """
        
        return q     
    
    
class query_top_artists( query ):
    def __init__(self):
        super( query_top_dr , self ).__init__()
        self.keys = [ "mean_dr" , "artist" , "track_cnt" ]
        
    def get_query(self):
        q = """
        select artist, mean_dr , track_cnt from 
        ( 
            select artist.name as artist , avg( dr.dr ) as mean_dr , count( track.id ) as track_cnt
               from track inner join DR_Track on DR_Track.idtrack = track.id 
                      inner join dr on dr.id = DR_Track.iddr 
                      inner join Artist_Track on Artist_Track.idtrack = track.id
                      inner join Artist on Artist.id = Artist_Track.IdArtist
                      group by artist                  
        )
        where track_cnt >= ? 
        order by mean_dr desc  ;
        """
        
        return q 



class query_dr_histogram( query ):
    def __init__(self):
        super( query_top_dr , self ).__init__()
        self.keys = [ "dr" , "dr_cnt" ]

    def exec_query(self):
        db = dr_database_singletone() ;
        return db.query( self.query , () , dict_factory_arg=my_dict_factory )
        
    def get_query(self):
        q = """
        select dr.dr as dr , count(dr.dr) as dr_cnt 
            from  DR_Track inner join dr on dr.id = DR_Track.iddr 
            group by (dr.dr) 
            order by (dr) ;
        """
        
        return q
    
    
class query_date_dr_evolution( query ):
    def __init__(self):
        super( query_top_dr , self ).__init__()
        self.keys = [ "date" , "mean" ]

    def exec_query(self):
        db = dr_database_singletone() ;
        return db.query( self.query , () , dict_factory_arg=my_dict_factory )
        
    def get_query(self):
        q = """
        select date.date as date , avg( dr.dr ) as mean
           from track inner join DR_Track on DR_Track.idtrack = track.id 
                  inner join dr on dr.id = DR_Track.iddr
                  inner join Date_Track on Date_Track.idtrack = track.id
                  inner join date on date.id = Date_Track.iddate
                  where dr.dr >= 0  
                  group by date 
                  order by date ;
        """
        
        return q
    

    
class query_dr_codec( query ):
    def __init__(self):
        super( query_top_dr , self ).__init__()
        self.keys = [ "codec" , "mean_dr" , "codec_freq" ]

    def exec_query(self):
        db = dr_database_singletone() ;
        return db.query( self.query , () , dict_factory_arg=my_dict_factory )
        
    def get_query(self):
        q = """
        select codec.name as codec , avg( dr.dr ) as mean_dr , count( Codec_Track.IdCodec ) as codec_freq 
           from track inner join DR_Track on DR_Track.idtrack = track.id 
                  inner join dr on dr.id = DR_Track.iddr 
                  inner join Codec_Track on Codec_Track.idtrack = track.id
                  inner join Codec on Codec.id = Codec_Track.IdCodec 
                  group by name 
                  order by mean_dr desc ;  
        """
        
        return q        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        