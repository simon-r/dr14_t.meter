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


class query:

    def __init__(self):
        self.keys = []
        self.__params = list([30])

    def append_parameter(self, p):
        self.__params.append(p)

    def set_parameter(self, i, p):
        self.__params[i] = p

    def get_parameter(self, i):
        return self.__params[i]

    def get_limit(self):
        return self.__params[0]

    def set_limit(self, limit):
        self.__params[0] = limit

    limit = property(get_limit, set_limit)

    def get_query(self):
        NotImplementedError(
            "%s : is virutal and must be overridden." % sys._getframe().f_code.co_name)

    def exec_query(self):
        db = dr_database_singletone().get()
        return db.query(self.get_query(), (self.limit,), dict_factory_arg=my_dict_factory)

    def get_col_keys(self):
        return self.keys


class query_top_dr(query):

    def __init__(self):
        query.__init__(self)
        self.keys = ["DR", "Title", "Artist", "Album"]

    def get_query(self):
        q = """
        select track.id as id , track.title as Title , dr.dr as DR , Album.title as Album , Artist.name as Artist 
           from track inner join DR_Track on DR_Track.idtrack = track.id 
                inner join dr on dr.id = DR_Track.iddr
                inner join Album_Track on Album_Track.idtrack = track.id
                inner join Album on Album.id = Album_Track.idalbum
                inner join Artist_Track on Artist_Track.idtrack = track.id
                inner join Artist on Artist.id = Artist_Track.IdArtist
                order by dr desc
                limit ? ;
        """

        return q


class query_top_albums_dr(query):

    def __init__(self):
        query.__init__(self)
        self.keys = ["DR", "Album_Title", "Artist"]

    def get_query(self):
        q = """
        select album.title as Album_Title , dr.dr as DR , album.id as id , Artist.name as Artist
           from album inner join DR_Album on DR_Album.idalbum = album.id 
                inner join dr on dr.id = DR_Album.iddr   
                inner join Artist_Album on album.id = Artist_Album.IdAlbum
                inner join Artist on Artist.Id = Artist_Album.IdArtist       
                order by dr desc
                limit ? ;
        """

        return q


class query_worst_albums_dr(query):

    def __init__(self):
        query.__init__(self)
        self.keys = ["DR", "Album_Title", "Artist"]

    def get_query(self):
        q = """
        select album.title as Album_Title , dr.dr as DR , album.id as id , Artist.name as Artist
           from album inner join DR_Album on DR_Album.idalbum = album.id
                inner join dr on dr.id = DR_Album.iddr
                inner join Artist_Album on album.id = Artist_Album.IdAlbum
                inner join Artist on Artist.Id = Artist_Album.IdArtist
                order by dr asc
                limit ? ;
        """

        return q


class query_worst_dr(query):

    def __init__(self):
        query.__init__(self)
        self.keys = ["DR", "Title", "Artist", "Album"]

    def get_query(self):
        q = """
        select track.id as id , track.title as Title , dr.dr as DR , Album.title as Album , Artist.name as Artist 
           from track inner join DR_Track on DR_Track.idtrack = track.id 
                inner join dr on dr.id = DR_Track.iddr
                inner join Album_Track on Album_Track.idtrack = track.id
                inner join Album on Album.id = Album_Track.idalbum
                inner join Artist_Track on Artist_Track.idtrack = track.id
                inner join Artist on Artist.id = Artist_Track.IdArtist
                order by dr asc
                limit ? ;
        """

        return q


class query_top_artists(query):

    def __init__(self):
        query.__init__(self)
        self.keys = ["Mean_DR", "Artist", "Track_Count"]
        self.append_parameter(10)

    def set_min_track(self, mt):
        self.set_parameter(1, mt)

    def get_min_track(self):
        return self.get_parameter(1)

    min_track = property(get_min_track, set_min_track)

    def exec_query(self):
        db = dr_database_singletone().get()
        return db.query(self.get_query(), (self.min_track, self.limit), dict_factory_arg=my_dict_factory)

    def get_query(self):
        q = """
        select Artist, Mean_DR , Track_Count from 
        ( 
            select artist.name as Artist , avg( dr.dr ) as Mean_DR , count( track.id ) as Track_Count
               from track inner join DR_Track on DR_Track.idtrack = track.id 
                      inner join dr on dr.id = DR_Track.iddr 
                      inner join Artist_Track on Artist_Track.idtrack = track.id
                      inner join Artist on Artist.id = Artist_Track.IdArtist
                      group by artist                  
        )
        where Track_Count >= ? 
        order by mean_dr desc  
        limit ? ;
        """

        return q


class query_dr_histogram(query):

    def __init__(self):
        query.__init__(self)
        self.keys = ["DR", "Freq"]

    def exec_query(self):
        db = dr_database_singletone().get()
        return db.query(self.get_query(), (), dict_factory_arg=my_dict_factory)

    def get_query(self):
        q = """
        select dr.dr as DR , count(dr.dr) as Freq 
            from  DR_Track inner join dr on dr.id = DR_Track.iddr
            where dr.dr >= 0 
            group by (dr.dr) 
            order by (dr) ;
        """

        return q


class query_date_dr_evolution(query):

    def __init__(self):
        query.__init__(self)
        self.keys = ["Date", "Mean"]

    def exec_query(self):
        db = dr_database_singletone().get()
        return db.query(self.get_query(), (), dict_factory_arg=my_dict_factory)

    def get_query(self):
        q = """
        select date.date as Date , avg( dr.dr ) as Mean
           from track inner join DR_Track on DR_Track.idtrack = track.id 
                  inner join dr on dr.id = DR_Track.iddr
                  inner join Date_Track on Date_Track.idtrack = track.id
                  inner join date on date.id = Date_Track.iddate
                  where dr.dr >= 0  
                  group by date 
                  order by date ;
        """

        return q


class query_dr_codec(query):

    def __init__(self):
        query.__init__(self)
        self.keys = ["Codec", "Mean_DR", "Codec_Freq"]

    def exec_query(self):
        db = dr_database_singletone().get()
        return db.query(self.get_query(), (), dict_factory_arg=my_dict_factory)

    def get_query(self):
        q = """
        select codec.name as Codec , avg( dr.dr ) as Mean_DR , count( Codec_Track.IdCodec ) as Codec_Freq 
           from track inner join DR_Track on DR_Track.idtrack = track.id 
                  inner join dr on dr.id = DR_Track.iddr 
                  inner join Codec_Track on Codec_Track.idtrack = track.id
                  inner join Codec on Codec.id = Codec_Track.IdCodec 
                  group by name 
                  order by mean_dr desc ;  
        """

        return q
