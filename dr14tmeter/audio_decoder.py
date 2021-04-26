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

import os
from dr14tmeter.audio_file_reader import *


class AudioDecoder:

    def __init__(self):
        # Attention!!! do not modify the order of this list!!!!
        # It is used for computing the sha1 of the track
        self.formats = ['.flac', '.mp3', '.ogg', '.opus', '.mp4',
                        '.m4a', '.wav', '.wv', '.ape', '.ac3', '.wma', '.dsf', '.dff']

        self._ext = -1

    def get_file_ext_code(self):
        return self._ext

    def read_track_new(self, file_name, target):

        (f, ext) = os.path.splitext(file_name)
        ext = ext.lower()

        if ext not in self.formats:
            return False

        af = AudioFileReader()

        if ext == '.mp3':
            af = Mp3FileReader()
        elif ext == '.flac':
            af = FlacFileReader()
        elif ext == '.ogg':
            af = OggFileReader()
        elif ext == '.opus':
            af = OpusFileReader()
        elif ext in ['.mp4', '.m4a']:
            af = Mp4FileReader()
        elif ext == '.wav':
            af = WavFileReader()
        elif ext == '.wav':
            af = WavPackFileReader()
        elif ext == '.wv':
            af = ApeFileReader()
        elif ext == '.ac3':
            af = Ac3FileReader()
        elif ext == '.wma':
            af = WmaFileReader()
        elif ext == '.dsf':
            af = DsfFileReader()
        elif ext == '.dff':
            af = DffFileReader()
        else:
            return False

        #af = PipeFileReader()

        self._ext = self.formats.index(ext)
        ret_f = af.read_audio_file_new(file_name, target)

        return ret_f
