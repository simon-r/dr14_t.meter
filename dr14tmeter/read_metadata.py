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


import subprocess
import sys
import os
import re
import hashlib
import numpy as np

from dr14tmeter.audio_decoder import AudioDecoder
from dr14tmeter.dr14_global import get_ffmpeg_cmd

if sys.version_info[0] == 2:
    import ConfigParser
else:
    import configparser as ConfigParser

from io import StringIO


# Test example !!!!!
# a = subprocess.check_output( [ "ffprobe" , "-show_format" , "/media/esterno_xfs/data/Musica/Musica/aavv/01-blitzkrieg_bop_160_lame_abr.mp3" ] , stderr=subprocess.STDOUT , shell=False )


class UnreadableAudioFileException(Exception):
    pass


class RetirveMetadata:

    def __init__(self):
        self._album = {}
        self._artist = {}
        self._tracks = {}
        self._disk_nr = []

        if get_ffmpeg_cmd() == "ffmpeg":
            self.__ffprobe_cmd = "ffprobe"
            self.__scan_file = self.scan_file_ffprobe
        elif get_ffmpeg_cmd() == "avconv":
            self.__ffprobe_cmd = "avprobe"
            self.__scan_file = self.scan_file_avprobe

        self.__scan_file = self.scan_file_orig

    def scan_dir(self, dir_name, files_list=None):

        self._album = {}
        self._tracks = {}
        self._artist = {}
        self._disk_nr = []

        if files_list == None:
            dir_name = os.path.abspath(dir_name)
            files_list = sorted(os.listdir(dir_name))

        ad = AudioDecoder()

        for file_name in files_list:

            (fn, ext) = os.path.splitext(file_name)
            full_file = os.path.join(dir_name, file_name)

            if ext in ad.formats:
                try:
                    self.scan_file(full_file)
                except UnreadableAudioFileException as uafe:
                    pass

    def get_scan_file(self):
        return self.__scan_file

    scan_file = property(get_scan_file)

    def match_repetitive_title(self, data_txt):
        re_flags = (re.MULTILINE | re.IGNORECASE | re.UNICODE)
        m = re.search(r"(\S[\S ]+\S)\s*;\s*\1", data_txt, re_flags)
        if m != None:
            return m.group(1)
        else:
            return data_txt

    def scan_file_orig(self, file_name):

        try:
            data_txt = subprocess.check_output([self.__ffprobe_cmd, "-show_format", "-show_streams", file_name],
                                               stderr=subprocess.STDOUT, shell=False)
        except:
            data_txt = "ffprobe ERROR"

        (foo, f_key) = os.path.split(file_name)

        if data_txt != "ffprobe ERROR":
            try:
                data_txt = data_txt.decode(encoding='UTF-8')
            except:
                data_txt = data_txt.decode(encoding='ISO-8859-1')
        else:
            self._tracks[f_key] = None
            raise UnreadableAudioFileException("problematic file: file_name")

        track = {}

        track['file_name'] = file_name

        re_flags = (re.MULTILINE | re.IGNORECASE | re.UNICODE)

        pattern = "[ \t\f\v]*([\S \t\f\v]+\S).*$"

        m = re.search(r"^\s*track\s*\:\s*(\d+).*$", data_txt, re_flags)
        if m != None:
            #track['nr'] = int( m.group(1) )
            track['track_nr'] = int(m.group(1))

        m = re.search(r"^\s*album\s*\:%s" % pattern, data_txt, re_flags)
        if m != None:
            #print( m.group(1) )
            track['album'] = self.match_repetitive_title(m.group(1))
            self._album.setdefault(track['album'], 0)
            self._album[track['album']] += 1

        m = re.search(r"^\s*title\s*\:%s" % pattern, data_txt, re_flags)
        if m != None:
            track['title'] = self.match_repetitive_title(m.group(1))

        m = re.search(r"^\s*artist\s*\:%s" % pattern, data_txt, re_flags)
        if m != None:
            track['artist'] = self.match_repetitive_title(m.group(1))
            self._artist.setdefault(track['artist'], 0)
            self._artist[track['artist']] += 1

        m = re.search(r"^\s*genre\s*\:%s" % pattern, data_txt, re_flags)
        if m != None:
            track['genre'] = self.match_repetitive_title(m.group(1))

        m = re.search(r"^\s*date\s*\:\s*(\d+).*$", data_txt, re_flags)
        if m != None:
            track['date'] = m.group(1)

        m = re.search(r"^\s*disc\s*:\s*(\d+).*$", data_txt, re_flags)
        if m != None:
            track['disk_nr'] = int(m.group(1))

        m = re.search(r"^size=\s*(\d+)\s*$", data_txt, re_flags)
        if m != None:
            track['size'] = m.group(1)

        m = re.search(r"^bit_rate=\s*(\d+)\s*$", data_txt, re_flags)
        if m != None:
            track['bitrate'] = m.group(1)

        m = re.search(r"^duration=\s*(\d+\.\d+)\s*$", data_txt, re_flags)
        if m != None:
            track['duration'] = float(m.group(1))

        self.__read_stream_info(data_txt, track)

        self._tracks[f_key] = track

    def scan_file_ffprobe(self, file_name):

        try:
            data_txt = subprocess.check_output([self.__ffprobe_cmd, "-show_format", "-show_streams", file_name],
                                               stderr=subprocess.STDOUT, shell=False)
        except:
            data_txt = "ffprobe ERROR"

        if data_txt != "ffprobe ERROR":
            try:
                data_txt = data_txt.decode(encoding='UTF-8')
            except:
                data_txt = data_txt.decode(encoding='ISO-8859-1')

        track = {}
        (foo, f_key) = os.path.split(file_name)

        track['file_name'] = file_name

        re_flags = (re.MULTILINE | re.IGNORECASE | re.UNICODE)

        m = re.search(r"\[FORMAT\](.*)\[/FORMAT\]",
                      data_txt, re_flags | re.DOTALL)
        if m != None:
            format_tags = m.group(1)
        else:
            self._tracks[f_key] = None
            raise UnreadableAudioFileException("problematic file: file_name")

        pattern = "[ \t\f\v]*([\S \t\f\v]+\S).*$"

        m = re.search(r"^TAG:track=\s*(\d+).*$", format_tags, re_flags)
        if m != None:
            track['track_nr'] = int(m.group(1))

        m = re.search(r"^TAG:disc=\s*(\d+).*$", format_tags, re_flags)
        if m != None:
            track['disk_nr'] = int(m.group(1))
            self._disk_nr.append(int(int(m.group(1))))

        m = re.search(r"^TAG:GENRE=%s" % pattern, format_tags, re_flags)
        if m != None:
            track['genre'] = m.group(1)

        m = re.search(r"^TAG:DATE=\s*(\d+).*$", format_tags, re_flags)
        if m != None:
            track['date'] = m.group(1)

        m = re.search(r"^TAG:ARTIST=%s" % pattern, format_tags, re_flags)
        if m != None:
            self._artist.setdefault(m.group(1), 0)
            self._artist[m.group(1)] += 1
            track['artist'] = m.group(1)

        m = re.search(r"^TAG:TITLE=%s" % pattern, format_tags, re_flags)
        if m != None:
            track['title'] = m.group(1)

        m = re.search(r"^TAG:ALBUM=%s" % pattern, format_tags, re_flags)
        if m != None:
            self._album.setdefault(m.group(1), 0)
            self._album[m.group(1)] += 1
            track['album'] = m.group(1)

        m = re.search(r"^size=\s*(\d+)\s*$", format_tags, re_flags)
        if m != None:
            track['size'] = m.group(1)

        m = re.search(r"^bit_rate=\s*(\d+)\s*$", format_tags, re_flags)
        if m != None:
            track['bitrate'] = m.group(1)

        self.__read_stream_info(data_txt, track)

        self._tracks[f_key] = track

    def scan_file_avprobe(self, file_name):
        try:
            data_txt = subprocess.check_output(
                [self.__ffprobe_cmd, "-show_format", "-show_streams", file_name], stderr=subprocess.STDOUT, shell=False)
        except:
            data_txt = "ffprobe ERROR"

        if data_txt != "ffprobe ERROR":
            try:
                data_txt = data_txt.decode(encoding='UTF-8')
            except:
                data_txt = data_txt.decode(encoding='ISO-8859-1')

        track = {}
        (foo, f_key) = os.path.split(file_name)

        track['file_name'] = file_name

        re_flags = (re.MULTILINE | re.IGNORECASE | re.UNICODE)

        m = re.search(r"(\[format\].*)", data_txt, re_flags | re.DOTALL)
        if m != None:
            format_tags = m.group(1)
        else:
            self._tracks[f_key] = None
            raise UnreadableAudioFileException("problematic file: file_name")

        buf = StringIO(format_tags)
        config = ConfigParser.ConfigParser()
        config.readfp(buf)

        try:
            track['title'] = config.get("format.tags", "title")
            self._album.setdefault(m.group(1), 0)
            self._album[m.group(1)] += 1
        except ConfigParser.NoOptionError:
            pass

        try:
            track['track_nr'] = config.getint("format.tags", "track")
        except ConfigParser.NoOptionError:
            pass

        try:
            track['disk_nr'] = config.get("format.tags", "disc")
            track['disk_nr'] = int(
                re.search("(\d+)", track['disk_nr']).group(1))
            self._disk_nr.append(track['disk'])
        except ConfigParser.NoOptionError:
            pass
        except:
            del track['disk_nr']

        try:
            track['genre'] = config.get("format.tags", "genre")
        except ConfigParser.NoOptionError:
            pass

        try:
            track['date'] = config.get("format.tags", "date")
        except ConfigParser.NoOptionError:
            pass

        try:
            track['artist'] = config.get("format.tags", "artist")
            self._artist.setdefault(m.group(1), 0)
            self._artist[m.group(1)] += 1
        except ConfigParser.NoOptionError:
            pass

        try:
            track['album'] = config.get("format.tags", "album")
        except ConfigParser.NoOptionError:
            pass

        try:
            track['size'] = str(int(config.getfloat("format.tags", "size")))
        except ConfigParser.NoOptionError:
            pass

        try:
            track['bitrate'] = str(
                int(config.getfloat("format.tags", "bit_rate")))
        except ConfigParser.NoOptionError:
            pass

        self.__read_stream_info(data_txt, track)

        self._tracks[f_key] = track

    def __read_stream_info(self, data_txt, track):

        re_flags = (re.MULTILINE | re.IGNORECASE | re.UNICODE)

        ##########################################
        # string examples:
        # Audio: flac, 44100 Hz, stereo, s16
        # Stream #0:0(und): Audio: alac (alac / 0x63616C61), 44100 Hz, 2 channels, s16, 634 kb/s
        # Stream #0:0(und): Audio: aac (LC) (mp4a / 0x6134706D), 44100 Hz, stereo, fltp, 255 kb/s (default
        # Stream #0:0: Audio: flac, 44100 Hz, stereo, s16

        m = re.search(r"Stream.*Audio:(.*)$", data_txt, re_flags)
        if m != None:
            fmt = m.group(1)

        fmt = re.split(",", fmt)

        #print( fmt )
        track['codec'] = re.search("\s*(\w+)", fmt[0], re_flags).group(1)
        track['sampling_rate'] = re.search(
            "\s*(\d+)", fmt[1], re_flags).group(1)
        track['channel'] = re.search(
            "^\s*([\S][\s|\S]*[\S])\s*$", fmt[2], re_flags).group(1)

        m = re.search("\((\d+) bit\)", fmt[3], re_flags)
        if m != None:
            track['bit'] = m.group(1)
        else:
            m = re.search("(\d+)", fmt[3], re_flags)
            if m != None:
                track['bit'] = m.group(1)
            else:
                track['bit'] = "16"

    def album_len(self):
        return len(self._tracks)

    def get_album_cnt(self):
        return len(self._album)

    def get_disk_nr(self):
        if len(self._disk_nr) > 0:
            return self._disk_nr[0]
        else:
            return None

    def get_album_list(self):
        return self._album

    def get_album_title(self):

        if len(self._album) > 1:
            return "Various"
        elif len(self._album) == 0:
            return None
        else:
            for k in self._album.keys():
                res = k
            return res

    def track_unreadable_failure(self, file_name):
        if self._tracks[file_name] == None:
            return True
        else:
            return False

    def get_album_sha1(self, title=None):

        if title == None:
            p_title = self.get_album_title()
        else:
            p_title = title

        if sys.version_info[0] == 2:
            str_conv = unicode
        else:
            str_conv = str

        key_string = str_conv("")
        #key_string = key_string + str_conv( p_title ) + str_conv( self.get_album_artist() )

        d = np.float64(0.0)
        s = np.float64(0.0)

        for track in sorted(self._tracks.keys()):

            if self._tracks[track] == None:
                continue

            if not self._tracks[track].get('size', False) or not self._tracks[track].get('codec', False):
                continue

            if title != None and not self._tracks[track]["album"] != title:
                continue

            #key_string = key_string + str_conv( track )
            key_string = key_string + str_conv(self._tracks[track]['size'])
            key_string = key_string + str_conv(self._tracks[track]['codec'])
            key_string = key_string + str_conv(self._tracks[track]['duration'])
            key_string = key_string + \
                str_conv(int(self._tracks[track]['bitrate']))
            d += np.float64(self._tracks[track]['duration'])
            s += np.float64(self._tracks[track]['size'])

        key_string = key_string + str_conv(d)
        key_string = key_string + str_conv(s)

        sa = np.frombuffer(bytearray(key_string.encode("utf8")), dtype=np.int8)

        #print( np.sum( sa ) )
        #print( len( sa ) )
        #print( len(key_string) )

        #print( bytearray( key_string.encode("utf8") ) )

        sha1 = hashlib.sha1(sa).hexdigest()
        #print( sha1 )
        return sha1

    def get_album_artist_old(self):

        if len(self._artist) > 1:
            return "Various Artists"
        elif len(self._artist) == 0:
            return None
        else:
            for k in self._artist.keys():
                res = k
            return res

    def get_album_artist(self, album=None):

        if album == None:
            return [self.get_album_artist_old()]

        artists = []
        for track in self._tracks.keys():
            if track["album"] == album:
                if not track["artist"] in artists:
                    artists.append(track["artist"])

        return artists

    def get_value(self, file_name, field):

        f = self._tracks.get(file_name, None)

        if f == None:
            return None

        return f.get(field, None)
