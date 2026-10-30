#!/usr/bin/python

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


from dr14tmeter.parse_args import parse_args
from dr14tmeter.dynamic_range_meter import DynamicRangeMeter
from dr14tmeter.table import *
from dr14tmeter.audio_analysis import *
from dr14tmeter.database import dr_database_singletone
from dr14tmeter.dr14_global import dr14_version, TestVer, test_new_version, get_home_url, get_new_version, get_exe_name
from dr14tmeter.dr14_utils import *
from dr14tmeter.out_messages import *
from dr14tmeter import ansi
from dr14tmeter.dr14_config import *
from dr14tmeter.database_utils import *

import os
import subprocess
import sys
import logging
import numpy


def invite_database():
    # a hint about the local DR database, printed before the analysis
    color = ansi.enabled(sys.stderr)

    def st(txt, *names):
        return ansi.style(txt, *names) if color else txt

    exe = get_exe_name()

    if not database_exists() or not db_is_enabled():
        print_msg(st(" Use the local DR database!", "bold", "magenta"))
        print_msg(" Store every result and query it later: the best and worst tracks,")
        print_msg(" albums and artists, the DR histogram, the DR evolution ...")
        print_msg(" To enable it run:  %s" % st("%s --enable_database" % exe, "bold"))
        print_msg(" More details: https://github.com/simon-r/dr14_t.meter/blob/master/how_to_use.md")
    else:
        print_msg(" %s the local DR database is enabled, run %s to query it" % (
            st("Tip:", "bold", "magenta"), st("%s -q" % exe, "bold")))

    print_msg("")


def main():

    options = parse_args()

    if options.version:
        print_msg(dr14_version())
        return

    init_log(logging.DEBUG)
    logging.disable(logging.INFO)

    numpy.seterr(all='ignore')

    #print( options )

    if options.enable_database:
        enable_database()
        return

    if options.disable_database:
        enable_db(False)
        print_msg("The local DR database is disabled! ")
        return

    if options.dump_database:
        db = dr_database_singletone().get()
        db.dump()
        return

    if db_is_enabled():
        db = dr_database_singletone().get()
        f = db.is_db_valid()

        if not f:
            print_err("It seems that there is some problem with the db ... ")
            fix_problematic_database()
            return

        try:
            db.upgrade_db()
        except Exception as e:
            print_err(str(e))
            return

    if options.query != None:

        if not database_exists():
            print_err("Error: The database does not exist")
            print_err("Error: type dr14_tmeter -q for more info.")
            return

        if len(options.query) == 0:
            query_helper()
            return

        if options.query[0] not in ["help", "top", "top_alb",
                                    "worst", "worst_alb", "top_art",
                                    "artist", "album", "hist", "evol", "codec", "info", "genres"]:

            print_err("Error: -q invalid parameter .")
            print_err("Error: type dr14_tmeter -q for more info.")
            return

        if options.query[0] in ["artist", "album"] and (
                len(options.query) not in [2, 3] or
                (len(options.query) == 3 and not options.query[2].isdigit())):

            print_err("usage: -q %s \"%s NAME\" [#nr] ." %
                      (options.query[0], options.query[0].upper()))
            print_err("names containing spaces must be quoted.")
            return

        table_code = database_exec_query(options)

        if table_code is not None:
            print_out(table_code)

        return

    if options.path_name != None:
        path_name = os.path.abspath(options.path_name)
    else:
        path_name = os.path.abspath('.')

    if not(os.path.exists(path_name)):
        print_msg("Error: The input directory \"%s\"  does not exist!" % path_name)
        return

    if options.out_dir and not(os.path.exists(options.out_dir)):
        print_msg(
            "Error (-o): The target directory \"%s\"  does not exist! " % options.out_dir)
        return

    if options.quiet:
        set_quiet_msg()

    if not options.quiet and not options.skip_version_check:
        l_ver = TestVer()
        l_ver.start()

    print_msg(path_name)
    print_msg("")

    invite_database()

    if options.recursive:
        subdirlist = list_rec_dirs(path_name)
    else:
        subdirlist = []
        subdirlist.append(path_name)

    if run_analysis_opt(options, path_name):
        return 1

    if options.scan_file:

        dr = DynamicRangeMeter()

        dr.write_to_local_db(db_is_enabled())

        r = dr.scan_file(path_name)

        if r == 1:
            print_out("")
            print_out(dr.res_list[0]['file_name'] + " :")
            print_out("DR      = %d" % dr.res_list[0]['dr14'])
            print_out("Peak dB = %.2f" % dr.res_list[0]['dB_peak'])
            print_out("Rms dB  = %.2f" % dr.res_list[0]['dB_rms'])
            return 1
        else:
            print_msg("Error: invalid audio file")
            return 0

    if options.out_dir == "":
        out_dir = None
    else:
        out_dir = options.out_dir

    if options.append and out_dir == None:
        out_dir = path_name

    if options.files_list:
        (success, clock, r) = scan_files_list(
            options.path_name, options, out_dir)
    else:
        (success, clock, r) = scan_dir_list(subdirlist, options, out_dir)

    if success:
        print_msg("Success! ")
        print_msg("Elapsed time: %2.2f sec" % clock)

    if sys.platform.startswith('linux') or sys.platform.startswith('darwin'):
        subprocess.call("stty sane", shell=True)

    if not success:
        if options.files_list:
            print_err("no valid audio files found in the list")
        else:
            print_err("no valid audio files found in \"%s\"" % path_name)
        print_msg("Usage: %s [options] path_name  (type %s --help for more details)" %
                  (get_exe_name(), get_exe_name()))
        sys.exit(1)

    if test_new_version():
        print_msg(
            "\n----------------------------------------------------------------------")
        print_msg(" A new version of dr14_t.meter [ %s ] is available for download"
                  " \n please visit: %s" % (
                      get_new_version(), get_home_url()))

        print_msg(
            "----------------------------------------------------------------------\n")

    return r


if __name__ == '__main__':
    main()
