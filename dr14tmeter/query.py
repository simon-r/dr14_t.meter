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


import datetime
import shutil
import struct
import sys
import unicodedata

from dr14tmeter import ansi
from dr14tmeter.console_plot import line_plot
from dr14tmeter.database import dr_database_singletone
from dr14tmeter.table import histogram_bar, wrap_text


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

    def get_plot(self, res):
        # console plot shown after the table of the results, if any
        return ""

    def get_highlight(self, res):
        # {column: cell texts} to show in green in the table, if any
        return {}


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
        select id, Artist, Mean_DR , Track_Count from 
        ( 
            select artist.id as id , artist.name as Artist , round( avg( dr.dr ) , 1 ) as Mean_DR , count( track.id ) as Track_Count
               from track inner join DR_Track on DR_Track.idtrack = track.id 
                      inner join dr on dr.id = DR_Track.iddr 
                      inner join Artist_Track on Artist_Track.idtrack = track.id
                      inner join Artist on Artist.id = Artist_Track.IdArtist
                      group by artist.id
        )
        where Track_Count >= ? 
        order by mean_dr desc  
        limit ? ;
        """

        return q


def normalize_name(name):
    # names are compared ignoring the case, the accents and the extra spaces:
    # "bjork" is the same as "Björk"
    name = unicodedata.normalize("NFKD", name.casefold())
    name = "".join(c for c in name if not unicodedata.combining(c))
    return " ".join(name.split())


def edit_distance(a, b, substring=False):
    # the minimal number of inserted, deleted, replaced or swapped (adjacent)
    # characters that turn a into b. With substring=True it is the distance
    # between a and the closest substring of b, so the characters of b before
    # and after the match are free: "floid" is at distance 1 from "Pink Floyd"
    m = len(a)
    prev2 = None
    prev = list(range(m + 1))
    best = m

    for j in range(1, len(b) + 1):
        col = [0 if substring else j] + [0] * m
        for i in range(1, m + 1):
            d = prev[i - 1] + (a[i - 1] != b[j - 1])
            if prev[i] + 1 < d:
                d = prev[i] + 1
            if col[i - 1] + 1 < d:
                d = col[i - 1] + 1
            if (i > 1 and j > 1 and a[i - 1] == b[j - 2] and
                    a[i - 2] == b[j - 1] and prev2[i - 2] + 1 < d):
                d = prev2[i - 2] + 1
            col[i] = d

        if col[m] < best:
            best = col[m]
        prev2, prev = prev, col

    return best if substring else prev[m]


def closest_names(name, rows, max_names=10):
    # rows are ( Id , Name , ... ), the result are the rows whose name is close
    # to the given one, as ( distance , row ), the closest first. The names
    # containing the given one have distance 0 and are all returned, the other
    # ones fill the list up to max_names
    key = normalize_name(name)

    # one typo every 5 characters: a short name with typos would be close to
    # too many names ( "moon" to "Paul Simon" , "Ramones" , ... )
    max_dist = len(key) // 5

    found = []
    for row in rows:
        if row[1] is None:
            continue

        n = normalize_name(row[1])
        if key in n:
            d = 0
        elif max_dist > 0:
            d = edit_distance(key, n, substring=True)
        else:
            continue

        if d <= max_dist:
            # equally close names: the one closest as a whole comes first
            found.append((d, edit_distance(key, n), n, row))

    found.sort(key=lambda f: f[:3])

    exact = [f for f in found if f[0] == 0]
    found = exact + found[len(exact):max(max_names, len(exact))]

    return [(f[0], f[3]) for f in found]


def find_artists(name):
    # the ( distance , ( Id , Name ) ) of the artists whose name is close to
    # the given one: "pink" finds both "Pink" and "Pink Floyd", "metalica"
    # finds "Metallica"
    db = dr_database_singletone().get()
    q = "select Id , Name from Artist ;"
    return closest_names(name, db.query(q))


def find_albums(title):
    # the ( distance , ( Id , Title , Artist ) ) of the albums whose title is
    # close to the given one
    db = dr_database_singletone().get()
    q = """
    select Album.Id , Album.Title , Artist.Name
        from Album left join Artist_Album on Artist_Album.IdAlbum = Album.Id
             left join Artist on Artist.Id = Artist_Album.IdArtist ;
    """
    return closest_names(title, db.query(q))


class query_selection(query):
    # a query restricted to the selected artists or albums

    def __init__(self, ids=()):
        query.__init__(self)
        self.append_parameter(list(ids))

    def set_ids(self, ids):
        self.set_parameter(1, list(ids))

    def get_ids(self):
        return self.get_parameter(1)

    ids = property(get_ids, set_ids)

    def get_ids_list(self):
        # the ids are written in the query, so that any number of artists or
        # albums can be selected without hitting the sqlite limit on the
        # parameters
        return " , ".join("%d" % int(i) for i in self.ids)


class query_artist_albums(query_selection):

    def __init__(self, artist_ids=()):
        query_selection.__init__(self, artist_ids)
        self.keys = ["DR", "Album_Title", "Artist"]

    def get_query(self):
        q = """
        select album.title as Album_Title , dr.dr as DR , album.id as id , Artist.name as Artist
           from album inner join DR_Album on DR_Album.idalbum = album.id
                inner join dr on dr.id = DR_Album.iddr
                inner join Artist_Album on album.id = Artist_Album.IdAlbum
                inner join Artist on Artist.Id = Artist_Album.IdArtist
                where Artist.Id in ( %s )
                order by dr desc , Album_Title
                limit ? ;
        """ % self.get_ids_list()

        return q


def artist_albums(artist_id):
    # the albums of an artist: rows with id, Album_Title and DR
    # an artist without albums gets the list of his tracks, with Album_Title
    # set to the track title and kind set to "track"
    q = query_artist_albums([artist_id])
    q.limit = 1000
    rows = q.exec_query()
    if rows:
        return rows

    q = query_artist_tracks([artist_id])
    q.limit = 1000
    rows = q.exec_query()
    for r in rows:
        r["Album_Title"] = r["Title"]
        r["kind"] = "track"
    return rows


def album_tracks(album_id):
    # the tracks of an album: rows with id, Album_Title (the title) and DR
    q = query_album_tracks([album_id])
    q.limit = 1000
    rows = q.exec_query()
    for r in rows:
        r["Album_Title"] = r["Title"]
        r["kind"] = "track"
    return rows


def artist_item_details(item):
    # the details of an item of artist_albums
    if item.get("kind") == "track":
        return track_details(item["id"])
    return album_details(item["id"])


class query_artist_tracks(query_selection):

    def __init__(self, artist_ids=()):
        query_selection.__init__(self, artist_ids)
        self.keys = ["DR", "Title", "Album", "Artist"]

    def get_query(self):
        # the tracks without an album are shown too
        q = """
        select track.id as id , track.title as Title , dr.dr as DR , Album.title as Album , Artist.name as Artist
           from track inner join DR_Track on DR_Track.idtrack = track.id
                inner join dr on dr.id = DR_Track.iddr
                inner join Artist_Track on Artist_Track.idtrack = track.id
                inner join Artist on Artist.id = Artist_Track.IdArtist
                left join Album_Track on Album_Track.idtrack = track.id
                left join Album on Album.id = Album_Track.idalbum
                where Artist.Id in ( %s )
                order by dr desc , Album , track.track_nr
                limit ? ;
        """ % self.get_ids_list()

        return q


class query_albums(query_selection):

    def __init__(self, album_ids=()):
        query_selection.__init__(self, album_ids)
        self.keys = ["DR", "Album_Title", "Artist"]

    def get_query(self):
        # the albums without an artist are shown too
        q = """
        select album.title as Album_Title , dr.dr as DR , album.id as id , Artist.name as Artist
           from album inner join DR_Album on DR_Album.idalbum = album.id
                inner join dr on dr.id = DR_Album.iddr
                left join Artist_Album on album.id = Artist_Album.IdAlbum
                left join Artist on Artist.Id = Artist_Album.IdArtist
                where album.Id in ( %s )
                order by dr desc , Album_Title
                limit ? ;
        """ % self.get_ids_list()

        return q


class query_album_tracks(query_selection):

    def __init__(self, album_ids=()):
        query_selection.__init__(self, album_ids)
        self.keys = ["Track_Nr", "DR", "Title", "Album", "Artist"]

    def get_query(self):
        # the tracks are in the order of the album
        q = """
        select track.id as id , track.track_nr as Track_Nr , track.title as Title , dr.dr as DR ,
               Album.title as Album , Artist.name as Artist
           from track inner join DR_Track on DR_Track.idtrack = track.id
                inner join dr on dr.id = DR_Track.iddr
                inner join Album_Track on Album_Track.idtrack = track.id
                inner join Album on Album.id = Album_Track.idalbum
                left join Artist_Track on Artist_Track.idtrack = track.id
                left join Artist on Artist.id = Artist_Track.IdArtist
                where Album.Id in ( %s )
                order by Album , Album.Id , track.track_nr , Title
                limit ? ;
        """ % self.get_ids_list()

        return q


def track_details(track_id):
    # the metadata of a track as a list of ( label , value ), None if missing
    db = dr_database_singletone().get()
    q = """
    select Track.title as Title, Track.track_nr as Track_Nr, Track.duration as Duration,
           Track.rms as Rms, Track.peak as Peak, Track.bit as Bit, Track.bitrate as Bitrate,
           Track.sampling_rate as Sampling_Rate, Track.size as Size, Track.sha1 as Sha1,
           dr.dr as DR, Codec.Name as Codec, Genre.Name as Genre, Date.Date as Date,
           Artist.Name as Artist, Album.Title as Album
        from Track
            left join DR_Track on DR_Track.IdTrack = Track.Id
            left join DR on DR.Id = DR_Track.IdDr
            left join Codec_Track on Codec_Track.IdTrack = Track.Id
            left join Codec on Codec.Id = Codec_Track.IdCodec
            left join Genre_Track on Genre_Track.IdTrack = Track.Id
            left join Genre on Genre.Id = Genre_Track.IdGenre
            left join Date_Track on Date_Track.IdTrack = Track.Id
            left join Date on Date.Id = Date_Track.IdDate
            left join Artist_Track on Artist_Track.IdTrack = Track.Id
            left join Artist on Artist.Id = Artist_Track.IdArtist
            left join Album_Track on Album_Track.IdTrack = Track.Id
            left join Album on Album.Id = Album_Track.IdAlbum
        where Track.Id = ? ;
    """
    rows = db.query(q, (track_id,), dict_factory_arg=my_dict_factory)
    if len(rows) == 0:
        return []
    r = rows[0]

    def fmt(key, f=str):
        v = r[key]
        # rms is stored as the raw bytes of a float32
        if isinstance(v, (bytes, bytearray)):
            v = struct.unpack("<f", v)[0] if len(v) == 4 else struct.unpack("<d", v)[0]
        return "" if v is None else f(v)

    return [("Title", fmt("Title")),
            ("Artist", fmt("Artist")),
            ("Album", fmt("Album")),
            ("Track nr", fmt("Track_Nr")),
            ("Genre", fmt("Genre")),
            ("Date", fmt("Date")),
            ("DR", fmt("DR")),
            ("RMS", fmt("Rms", lambda v: "%.2f dB" % v)),
            ("Peak", fmt("Peak", lambda v: "%.2f dB" % v)),
            ("Length", fmt("Duration", seconds_to_str)),
            ("Codec", fmt("Codec")),
            ("Bit", fmt("Bit")),
            ("Bitrate", fmt("Bitrate", lambda v: "%d kbps" % (v // 1000 if v > 10000 else v))),
            ("Sampling", fmt("Sampling_Rate", lambda v: "%d Hz" % v)),
            ("Size", fmt("Size", lambda v: "%.2f MB" % (v / 1048576.0))),
            ("SHA1", fmt("Sha1"))]


def album_details(album_id):
    # the metadata of an album, with the numbered list of all its tracks
    db = dr_database_singletone().get()
    head = db.query("""
    select Album.Title as Title, dr.dr as DR, Date.Date as Date, Genre.Name as Genre,
           group_concat( distinct Artist.Name ) as Artist
        from Album
            left join DR_Album on DR_Album.IdAlbum = Album.Id
            left join DR on DR.Id = DR_Album.IdDr
            left join Artist_Album on Artist_Album.IdAlbum = Album.Id
            left join Artist on Artist.Id = Artist_Album.IdArtist
            left join Album_Track on Album_Track.IdAlbum = Album.Id
            left join Date_Track on Date_Track.IdTrack = Album_Track.IdTrack
            left join Date on Date.Id = Date_Track.IdDate
            left join Genre_Track on Genre_Track.IdTrack = Album_Track.IdTrack
            left join Genre on Genre.Id = Genre_Track.IdGenre
        where Album.Id = ? ;
    """, (album_id,), dict_factory_arg=my_dict_factory)
    tracks = db.query("""
    select Track.title as Title, Track.track_nr as Track_Nr, Track.duration as Duration,
           dr.dr as DR
        from Album_Track inner join Track on Track.Id = Album_Track.IdTrack
            left join DR_Track on DR_Track.IdTrack = Track.Id
            left join DR on DR.Id = DR_Track.IdDr
        where Album_Track.IdAlbum = ?
        order by Track.track_nr , Track.title ;
    """, (album_id,), dict_factory_arg=my_dict_factory)
    if len(head) == 0:
        return []
    r = head[0]

    def txt(v):
        return "" if v is None else str(v)

    total = sum(t["Duration"] or 0 for t in tracks)
    items = []
    for t in tracks:
        extra = []
        if t["DR"] is not None:
            extra.append("DR%d" % t["DR"])
        if t["Duration"]:
            extra.append(seconds_to_str(t["Duration"]))
        items.append("%s%s" % (t["Title"] or "", " (%s)" % ", ".join(extra) if extra else ""))

    return [("Album", txt(r["Title"])),
            ("Artist", txt(r["Artist"])),
            ("Genre", txt(r["Genre"])),
            ("Date", txt(r["Date"])),
            ("DR", txt(r["DR"])),
            ("Tracks", "%d" % len(tracks)),
            ("Length", seconds_to_str(total)),
            ("Track list", items)]


class query_dr_histogram(query):

    def __init__(self):
        query.__init__(self)
        self.keys = ["DR", "Freq", "Histogram"]

    def exec_query(self):
        db = dr_database_singletone().get()
        res = db.query(self.get_query(), (), dict_factory_arg=my_dict_factory)

        if len(res) == 0:
            return res

        freq = dict((r["DR"], r["Freq"]) for r in res)
        max_freq = max(freq.values())

        # the longest bar takes half of the console width
        width = shutil.get_terminal_size().columns // 2

        # the DR values in between that are not in the database are shown
        # as empty bins
        hist = []
        for dr in range(min(freq), max(freq) + 1):
            f = freq.get(dr, 0)
            hist.append({"DR": dr, "Freq": f,
                         "Histogram": histogram_bar(f, max_freq, width)})

        return hist

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

    # the dates before this year are considered invalid and are not plotted
    min_year = 1950

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

    def get_plot(self, res):
        # the invalid dates (broken tags, or before min_year) would squeeze
        # the time axis, so they are not plotted
        last_year = datetime.date.today().year + 1
        years = [r for r in res if self.min_year <= r["Date"] <= last_year]
        skipped = [str(r["Date"]) for r in res if r not in years]

        if len(years) == 0:
            return ""

        console = shutil.get_terminal_size()
        height = min(max(console.lines // 2, 8), 20)

        color = ansi.enabled()

        txt = "\n %s\n\n" % (
            ansi.style("Mean DR per year", "bold", "magenta") if color else "Mean DR per year")
        txt += line_plot([r["Date"] for r in years],
                         [r["Mean"] for r in years],
                         console.columns, height)

        if len(skipped) > 0:
            note = "Not plotted, invalid years (valid: %d-%d): %s" % (
                self.min_year, last_year, ", ".join(skipped))
            txt += "\n"
            for line in wrap_text(note, max(console.columns - 2, 20)):
                txt += " " + (ansi.style(line, "red") if color else line) + "\n"

        return txt


class query_dr_codec(query):

    def __init__(self):
        query.__init__(self)
        self.keys = ["Codec", "Mean_DR", "Codec_Freq"]

    def exec_query(self):
        db = dr_database_singletone().get()
        return db.query(self.get_query(), (), dict_factory_arg=my_dict_factory)

    def get_query(self):
        q = """
        select codec.name as Codec , round( avg( dr.dr ) , 1 ) as Mean_DR , count( Codec_Track.IdCodec ) as Codec_Freq 
           from track inner join DR_Track on DR_Track.idtrack = track.id 
                  inner join dr on dr.id = DR_Track.iddr 
                  inner join Codec_Track on Codec_Track.idtrack = track.id
                  inner join Codec on Codec.id = Codec_Track.IdCodec 
                  group by name 
                  order by mean_dr desc ;  
        """

        return q


def seconds_to_str(s):
    s = int(round(s))
    if s >= 3600:
        return "%d:%02d:%02d" % (s // 3600, (s % 3600) // 60, s % 60)
    return "%d:%02d" % (s // 60, s % 60)


def tracks_info():
    # one row per track: genre, length in seconds and DR (None if missing)
    db = dr_database_singletone().get()
    q = """
    select Track.duration as Duration, Genre.Name as Genre, dr.dr as DR
        from Track
            left join DR_Track on DR_Track.IdTrack = Track.Id
            left join DR on DR.Id = DR_Track.IdDR
            left join Genre_Track on Genre_Track.IdTrack = Track.Id
            left join Genre on Genre.Id = Genre_Track.IdGenre ;
    """
    rows = db.query(q, (), dict_factory_arg=my_dict_factory)

    for r in rows:
        r["Seconds"] = r["Duration"] or 0
        if r["DR"] is not None and r["DR"] < 0:
            r["DR"] = None

    return rows


class query_collection_info(query):

    good_dr = 14
    bad_dr = 7

    def __init__(self):
        query.__init__(self)
        self.keys = ["Property", "Value"]

    def exec_query(self):
        db = dr_database_singletone().get()
        rows = tracks_info()

        if len(rows) == 0:
            return []

        def count(table, where=""):
            return db.query("select count(*) as n from %s %s ;" % (table, where),
                            (), dict_factory_arg=my_dict_factory)[0]["n"]

        seconds = [r["Seconds"] for r in rows]
        genres = set(r["Genre"] for r in rows if r["Genre"])
        dr = sorted(r["DR"] for r in rows if r["DR"] is not None)

        info = [("Tracks", count("Track")),
                ("Albums", count("Album", "where Id > 0")),
                ("Artists", count("Artist")),
                ("Genres", len(genres)),
                ("Total length", seconds_to_str(sum(seconds))),
                ("Mean track length", seconds_to_str(sum(seconds) / len(seconds)))]

        if len(dr) > 0:
            mid = len(dr) // 2
            median = dr[mid] if len(dr) % 2 else (dr[mid - 1] + dr[mid]) / 2.0
            info += [("Mean DR", "%.2f" % (sum(dr) / float(len(dr)))),
                     ("Median DR", "%.1f" % median),
                     ("Min DR", dr[0]),
                     ("Max DR", dr[-1]),
                     ("Tracks with DR >= %d" % self.good_dr,
                      "%.1f%%" % (100.0 * len([d for d in dr if d >= self.good_dr]) / len(dr))),
                     ("Tracks with DR <= %d" % self.bad_dr,
                      "%.1f%%" % (100.0 * len([d for d in dr if d <= self.bad_dr]) / len(dr)))]

        return [{"Property": p, "Value": v} for (p, v) in info]


class query_genres(query):

    # genres highlighted as the best and the worst ones: the first and the
    # last n_best by mean DR, among the genres with at least min_track tracks
    n_best = 3
    min_track = 5

    def __init__(self):
        query.__init__(self)
        self.keys = ["Genre", "Tracks", "Mean_Length", "Mean_DR"]

    def exec_query(self):
        per_genre = {}
        for r in tracks_info():
            per_genre.setdefault(r["Genre"] or "(none)", []).append(r)

        res = []
        for genre, rows in per_genre.items():
            dr = [r["DR"] for r in rows if r["DR"] is not None]
            res.append({"Genre": genre,
                        "Tracks": len(rows),
                        "Mean_Length": seconds_to_str(
                            sum(r["Seconds"] for r in rows) / len(rows)),
                        "Mean_DR": sum(dr) / float(len(dr)) if dr else ""})

        res.sort(key=lambda r: (-r["Tracks"], r["Genre"]))
        return res[:self.limit]

    def get_highlight(self, res):
        # the genres with the best (green) and the worst (red) mean DR,
        # ignoring the ones with few tracks
        ranked = [r for r in res
                  if r["Mean_DR"] != "" and r["Tracks"] >= self.min_track]
        ranked.sort(key=lambda r: -r["Mean_DR"])

        rows = dict((r["Genre"], "red") for r in ranked[-self.n_best:])
        rows.update((r["Genre"], "green") for r in ranked[:self.n_best])

        return {"key": "Genre", "cols": ["Genre", "Mean_DR"], "rows": rows}
