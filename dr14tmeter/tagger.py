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

from dr14tmeter import dr14_global
import os
from mutagen.mp3 import MP3
from mutagen.flac import FLAC
from mutagen.oggvorbis import OggVorbis
from mutagen.oggopus import OggOpus
from mutagen.monkeysaudio import MonkeysAudio
from mutagen.mp4 import MP4
from mutagen.id3 import ID3, TXXX
from dr14tmeter.audio_file_reader import *


class Tagger:

    def __init__(self):
        self.formats = ['.flac', '.mp3', '.ogg', '.opus', '.mp4',
                        '.m4a', '.wav', '.ape', '.ac3', '.wma']
        self.dir_name = ''
        self._ext = -1
    
    def write_dr_tags(self, dr):

        if not dr14_global.test_mutagen("Tagging"):
            sys.exit(1)

        self.dir_name = dr.dir_name
        
        for item in dr.res_list:
            self.read_track_new(item)

    def get_file_ext_code(self):
        return self._ext

    def read_track_new(self, item):

        (f, ext) = os.path.splitext(item['file_name'])
        ext = ext.lower()

        if ext not in self.formats:
            return False

        audio = None
        filename = self.dir_name + os.sep + item['file_name']

        if ext == '.mp3':
            audio = MP3(filename)
            audio.add_tags
        elif ext == '.flac':
            audio = FLAC(filename)
        elif ext == '.ogg':
            audio = OggVorbis(filename)
        elif ext == '.opus':
            audio = OggOpus(filename)
        elif ext in ['.mp4', '.m4a']:
            audio = MP4(filename)
        elif ext == '.wav':
            raise Exception("Tagging .wav files not supported")
        elif ext == '.ape':
            audio = MonkeysAudio(filename)
        elif ext == '.ac3':
            raise Exception("Tagging .ac3 files not supported")
        elif ext == '.wma':
            raise Exception("Tagging .wma files not supported")
        else:
            return False

        if isinstance(audio, MP3):
            audio.tags.add(TXXX(encoding=3, desc=u"DR", text=[str(item["dr14"])]))
        else:
            audio["DR"] = [str(item["dr14"])]
        
        audio.save()
        
        self._ext = self.formats.index(ext)

        return True