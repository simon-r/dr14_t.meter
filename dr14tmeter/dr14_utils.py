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


from dr14tmeter.tagger import Tagger
import multiprocessing
import os
import tempfile
import fileinput
import time
import sys

from dr14tmeter import dr14_global
from dr14tmeter import dr14_config as config
from dr14tmeter import audio_analysis as aa
from dr14tmeter.dynamic_range_meter import DynamicRangeMeter, TextTable, BBcodeTable, HtmlTable, MediaWikiTable
from dr14tmeter.out_messages import print_msg


def scan_files_list(input_file, options, out_dir):
    if out_dir is None:
        out_dir = tempfile.gettempdir()
    else:
        out_dir = os.path.abspath(out_dir)

    a = time.time()

    if input_file is None:
        input_file = '-'

    files_list = []

    for line in fileinput.input(input_file):
        files_list.append(os.path.abspath(line.rstrip()))

    dr = DynamicRangeMeter()
    dr.write_to_local_db(config.db_is_enabled())

    r = dr.scan_mp(files_list=files_list, thread_cnt=get_thread_cnt())

    if r == 0:
        success = False
    else:
        write_results(dr, options, out_dir, "")

    if options.tag:
        tagger = Tagger()
        tagger.write_dr_tags(dr)

        success = True

    clock = time.time() - a
    return success, clock, r


def scan_dir_list(subdirlist, options, out_dir):
    a = time.time()

    success = False
    r = 0

    for cur_dir in subdirlist:
        dr = DynamicRangeMeter()
        dr.write_to_local_db(config.db_is_enabled())

        print_msg("\n------------------------------------------------------------ ")
        print_msg("> Scan Dir: %s \n" % cur_dir)

        if options.disable_multithread:
            r = dr.scan_dir(cur_dir)
        else:
            cpu = get_thread_cnt()
            r = dr.scan_mp(cur_dir, cpu)

        if options.tag:
            tagger = Tagger()
            tagger.write_dr_tags(dr)

        if r == 0:
            continue
        else:
            success = True

        write_results(dr, options, out_dir, cur_dir)

    clock = time.time() - a

    return success, clock, r


def get_thread_cnt():
    cpu = multiprocessing.cpu_count()
    cpu = max(2, int(round(cpu / 2)))
    return cpu


def list_rec_dirs(basedir, subdirlist=None):
    if subdirlist is None:
        subdirlist = [basedir]

    for item in os.listdir(basedir):
        item = os.path.join(basedir, item)
        if os.path.isdir(item):
            item = os.path.abspath(item)
            # print_msg( item )
            subdirlist.append(item)
            list_rec_dirs(item, subdirlist)

    return subdirlist


def write_results(dr, options, out_dir, cur_dir):
    table_format = not options.basic_table

    if out_dir is None:
        full_out_dir = os.path.join(cur_dir)
    else:
        full_out_dir = out_dir

    print_msg("DR = " + str(dr.dr14))

    if not (os.access(full_out_dir, os.W_OK)):
        full_out_dir = tempfile.gettempdir()
        print_msg(
            "--------------------------------------------------------------- ")
        print_msg("- ATTENTION !")
        print_msg(
            "- You do not have the write permission for the directory: %s " % full_out_dir)
        print_msg(
            "- The result files will be written in the tmp dir: %s " % full_out_dir)
        print_msg(
            "--------------------------------------------------------------- ")

    if options.print_std_out:
        dr.fwrite_dr("", TextTable(), table_format, True)

    if options.turn_off_out:
        return

    all_tables = False
    if 'a' in options.out_tables:
        all_tables = True

    tables_list = {
        'b': ["dr14_bbcode.txt", BBcodeTable()],
        't': ["dr14-DR"+str(dr.dr14)+".txt",TextTable()],
        'h': ["dr14.html", HtmlTable()],
        'w': ["dr14_mediawiki.txt", MediaWikiTable()]
    }

    out_list = ""

    dr.write_to_local_database()

    for code in tables_list.keys():
        if code in options.out_tables or all_tables:
            dr.fwrite_dr(os.path.join(full_out_dir, tables_list[code][0]), tables_list[code][1], table_format,
                         append=options.append, dr_database=options.dr_database)
            out_list += " %s " % tables_list[code][0]

    print_msg("")
    print_msg("- The full result has been written in the files: %s" % out_list)
    print_msg("- located in the directory: ")
    print_msg(full_out_dir)
    print_msg("")


def test_path_validity(path):
    if path in ["/", ""]:
        return False
    if os.access(path, os.W_OK):
        return True
    else:
        (h, t) = os.path.split(path)
        return test_path_validity(h)


def run_analysis_opt(options, path_name):
    flag = False

    if options.compress:
        if not dr14_global.test_compress_modules():
            sys.exit(1)

        print_msg("Start compressor:")
        comp = aa.AudioCompressor()
        comp.setCompressionModality(options.compress)
        comp.compute_track(path_name)
        flag = True

    if options.spectrogram:
        if not dr14_global.test_matplotlib_modules("Spectrogram"):
            sys.exit(1)

        print_msg("Start spectrogram:")
        spectr = aa.AudioSpectrogram()
        spectr.compute_track(path_name)
        flag = True

    if options.plot_track:
        if not dr14_global.test_matplotlib_modules("Plot track"):
            sys.exit(1)

        print_msg("Start Plot Track:")
        spectr = aa.AudioPlotTrack()
        spectr.compute_track(path_name)
        flag = True

    if options.plot_track_dst:
        if not dr14_global.test_matplotlib_modules("Plot track dst"):
            sys.exit(1)

        print_msg("Start Plot Track:")
        spectr = aa.AudioPlotTrackDistribution()
        spectr.compute_track(path_name)
        flag = True

    if options.histogram:
        if not dr14_global.test_hist_modules():
            sys.exit(1)

        print_msg("Start histogram:")
        hist = aa.AudioDrHistogram()
        hist.compute_track(path_name)
        flag = True

    if options.lev_histogram:
        if not dr14_global.test_hist_modules():
            sys.exit(1)

        print_msg("Start level histogram:")
        hist = aa.AudioLevelHistogram()
        hist.compute_track(path_name)
        flag = True

    if options.dynamic_vivacity:
        if not dr14_global.test_hist_modules():
            sys.exit(1)

        print_msg("Start Dynamic vivacity:")
        viva = aa.AudioDynVivacity()
        viva.compute_track(path_name)
        flag = True

    return flag
