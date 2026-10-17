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

import time
import os
import sys
import tempfile
import shutil
import subprocess
import re
import wave
import numpy


from dr14tmeter.out_messages import print_msg, dr14_log_info
from dr14tmeter.dr14_global import get_ffmpeg_cmd

#from _ftdi1 import NONE

# ffmpeg -i example.m4a -f wav pipe:1 > test.wav


class AudioFileReader:

    def __init__(self):

        self.__ffmpeg_cmd = get_ffmpeg_cmd()

        # False: resample to 44.1 kHz / 16 bit as the DR measurement expects
        # True: keep the source sample rate and resolution (analysis plots)
        self.native_rate = False

        if sys.platform.startswith('win'):
            self.__cmd = ".\\decoder\\%s " % self.get_cmd()
        else:
            self.__cmd = "%s " % self.get_cmd()

    def get_cmd(self):
        pass

    def get_ffmpeg_cmd(self):
        return self.__ffmpeg_cmd

    def get_cmd_options(self, file_name, tmp_file):
        pass

    def to_wav(self, file_name):

        full_command = self.__cmd

        (head, file) = os.path.split(file_name)
        tmp_dir = tempfile.gettempdir()
        tmp_file = os.path.join(tmp_dir, file) + ".wav"

        file_name = re.sub("(\"|`)", r"\\\1", file_name)
        tmp_file = re.sub("(\"|`)", r"_xyz_", tmp_file)

        full_command = full_command + " " + \
            self.get_cmd_options(file_name, tmp_file)

        r = subprocess.Popen(full_command, shell=True,
                            stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        stdout_data, stderr_data = r.communicate()

        if os.path.exists(tmp_file):
            return tmp_file
        else:
            return ""

    def read_audio_file_new(self, file_name, target):

        time_a = time.time()

        full_command = self.__cmd

        # unique temp dir: avoids collisions between same-named files/processes
        tmp_dir = tempfile.mkdtemp(prefix="dr14_")
        tmp_file = os.path.join(tmp_dir, "track.wav")

        file_name = re.sub(r"(\"|`|\$)", r"\\\1", file_name)

        full_command = full_command + " " + \
            self.get_cmd_options(file_name, tmp_file)

        r = subprocess.Popen(full_command, shell=True,
                             stdin=subprocess.DEVNULL,
                             stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        stdout_data, stderr_data = r.communicate()

        if os.path.exists(tmp_file):
            self.set_pcm_format_tag(tmp_file)
            ret_f = self.read_wav(tmp_file, target)
        elif r.returncode == 127:
            # shell: command not found (e.g. ffmpeg is not installed)
            print_msg(file_name + ": decoder not found, please install %s" %
                      (self.get_cmd() or "ffmpeg"))
            ret_f = False
        else:
            print_msg(file_name + ": unsupported encoder")
            ret_f = False

        shutil.rmtree(tmp_dir, ignore_errors=True)

        time_b = time.time()
        dr14_log_info(
            "AudioFileReader.read_audio_file_new: Clock: %2.8f" % (time_b - time_a))

        return ret_f

    def read_wav(self, file_name, target):

        time_a = time.time()

        convert_8_bit = numpy.float32(2**8 + 1.0)
        convert_16_bit = numpy.float32(2**15 + 1.0)
        convert_32_bit = numpy.float32(2**31 + 1.0)

        try:
            wave_read = wave.open(file_name, 'r')
            target.channels = wave_read.getnchannels()
            target.Fs = wave_read.getframerate()
            target.sample_width = wave_read.getsampwidth()

            nframes = wave_read.getnframes()
            #print_msg( file_name + "!!!!!!!!!!!!: " + str(target.channels) + " " + str(target.sample_width ) + " " + str( target.Fs ) + " " + str( nframes ) )

            X = wave_read.readframes(wave_read.getnframes())

            sample_type = "int%d" % (target.sample_width * 8)

            target.Y = numpy.frombuffer(X, dtype=sample_type).reshape(
                nframes, target.channels)

            wave_read.close()

            if sample_type == 'int16':
                target.Y = target.Y / (convert_16_bit)
            elif sample_type == 'int32':
                target.Y = target.Y / (convert_32_bit)
            else:
                target.Y = target.Y / (convert_8_bit)

            #print_msg( "target.Y: " + str(target.Y.dtype) )
        except:
            self.__init__()
            print_msg("Unexpected error: %s" % str(sys.exc_info()))
            print_msg("\n - ERROR ! ")
            return False

        time_b = time.time()
        dr14_log_info("AudioFileReader.read_wav: Clock: %2.8f" %
                      (time_b - time_a))

        return True

    # ffmpeg writes a WAVE_FORMAT_EXTENSIBLE header above 48 kHz or 16 bit,
    # which the wave module reads only from Python 3.12. When the sub-format
    # is integer PCM, the plain WAVE_FORMAT_PCM tag describes the same data.
    def set_pcm_format_tag(self, file_name):
        with open(file_name, 'r+b') as f:
            h = f.read(46)
            if h[12:16] == b'fmt ' and h[20:22] == b'\xfe\xff' and h[44:46] == b'\x01\x00':
                f.seek(20)
                f.write(b'\x01\x00')

    def get_generic_ffmpeg_options(self, file_name, tmp_file):
        if self.native_rate:
            out_fmt = "-c:a pcm_s32le"
        else:
            out_fmt = "-b:a 16 -ar 44100"
        return " -nostdin -i \"%s\" -vn %s -y \"%s\" -loglevel quiet " % (file_name, out_fmt, tmp_file)


class Mp3FileReader(AudioFileReader):

    def get_cmd(self):
        return "lame"

    def get_cmd_options(self, file_name, tmp_file):
        return "--silent " + "--decode " + "\"" + file_name + "\"" + " \"%s\" " % tmp_file


class FlacFileReader(AudioFileReader):

    def get_cmd(self):
        return self.get_ffmpeg_cmd()

    def get_cmd_options(self, file_name, tmp_file):
        return self.get_generic_ffmpeg_options(file_name, tmp_file)
        # return " -s " + "-d " + "\"" + file_name + "\"" + " -o \"%s\" " %
        # tmp_file


class Mp4FileReader(AudioFileReader):

    def get_cmd(self):
        return self.get_ffmpeg_cmd()

    def get_cmd_options(self, file_name, tmp_file):
        return self.get_generic_ffmpeg_options(file_name, tmp_file)


class OggFileReader(AudioFileReader):

    def get_cmd(self):
        return "oggdec"

    def get_cmd_options(self, file_name, tmp_file):
        return "--quiet " + "\"" + file_name + "\"" + " --output \"%s\"  " % tmp_file

class OpusFileReader(AudioFileReader):

    def get_cmd(self):
        return self.get_ffmpeg_cmd()

    def get_cmd_options(self, file_name, tmp_file):
        return self.get_generic_ffmpeg_options(file_name, tmp_file)

class ApeFileReader(AudioFileReader):

    def get_cmd(self):
        return self.get_ffmpeg_cmd()

    def get_cmd_options(self, file_name, tmp_file):
        return self.get_generic_ffmpeg_options(file_name, tmp_file)


class Ac3FileReader(AudioFileReader):

    def get_cmd(self):
        return self.get_ffmpeg_cmd()

    def get_cmd_options(self, file_name, tmp_file):
        return self.get_generic_ffmpeg_options(file_name, tmp_file)


class WmaFileReader(AudioFileReader):

    def get_cmd(self):
        return self.get_ffmpeg_cmd()

    def get_cmd_options(self, file_name, tmp_file):
        return self.get_generic_ffmpeg_options(file_name, tmp_file)


class WavFileReader(AudioFileReader):

    # read_wav handles only 16 and 32 bit integer PCM: decode any other
    # wav (24 bit, float) through ffmpeg like the other formats
    def read_audio_file_new(self, file_name, target):
        try:
            with wave.open(file_name, 'r') as wave_read:
                direct = wave_read.getsampwidth() in (2, 4)
        except Exception:
            direct = False

        if direct:
            return self.read_wav(file_name, target)
        return AudioFileReader.read_audio_file_new(self, file_name, target)

    def get_cmd(self):
        return self.get_ffmpeg_cmd()

    def get_cmd_options(self, file_name, tmp_file):
        return self.get_generic_ffmpeg_options(file_name, tmp_file)

class WavpackFileReader(AudioFileReader):

    def read_audio_file_new(self, file_name, target):
        return self.read_wavpack(file_name, target)

    def get_cmd(self):
        return ""

    def get_cmd_options(self, file_name, tmp_file):
        return ""

class DsfFileReader(AudioFileReader):

    def get_cmd(self):
        return self.get_ffmpeg_cmd()

    def get_cmd_options(self, file_name, tmp_file):
        return self.get_generic_ffmpeg_options(file_name, tmp_file)

class DffFileReader(AudioFileReader):

    def get_cmd(self):
        return self.get_ffmpeg_cmd()

    def get_cmd_options(self, file_name, tmp_file):
        return self.get_generic_ffmpeg_options(file_name, tmp_file)
