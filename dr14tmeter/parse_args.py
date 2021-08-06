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


import argparse


def parse_args():
    desc = "Compute the DR14 value of the audio files according to the algorithm "
    desc = desc + "described by the Pleasurize Music Foundation "
    desc = desc + "Visit: http://www.dynamicrange.de/"

    parser = argparse.ArgumentParser(description=desc)

    parser.add_argument("-1", "--disable_multithread",
                        action="store_true",
                        dest="disable_multithread",
                        help="Disable the multi-Core mode")

    parser.add_argument("-r", "--recursive",
                        action="store_true",
                        dest="recursive",
                        help="Scan recursively the subdirectories")

    parser.add_argument("-a", "--append",
                        action="store_true",
                        dest="append",
                        help="Append all results in a single file; it should be used in couple with -r")

    parser.add_argument("-b", "--basic_table",
                        action="store_true",
                        dest="basic_table",
                        help="Write the resulting tables in the basic format")

    parser.add_argument("-n", "--turn_off_out",
                        action="store_true",
                        dest="turn_off_out",
                        help="do not writes the output files")

    parser.add_argument("-p", "--print_std_out",
                        action="store_true",
                        dest="print_std_out",
                        help="writes the full result on the std_out")

    parser.add_argument("-o", "--outdir",
                        action="store",
                        dest="out_dir",
                        type=str,
                        help="Write the resultings files into the given directory")

    parser.add_argument("-t", "--tables",
                        action="store",
                        choices='htbwa',
                        dest="out_tables",
                        default="t",
                        help="Select the output files to be written. h=html t=text b=bbcode w=mediawiki a=all_formats")

    parser.add_argument("-f", "--file",
                        action='store_true',
                        dest="scan_file",
                        help="Compute the DR14 of a single file and exit")

    parser.add_argument("--enable_database",
                        action="store_true",
                        dest="enable_database",
                        help="Enable and create, if necessary, the local DR database")

    parser.add_argument("--disable_database",
                        action="store_true",
                        dest="disable_database",
                        help="Disable the local DR database")

    parser.add_argument("--dump_database",
                        action="store_true",
                        dest="dump_database",
                        help="Dump the local DR database")

    parser.add_argument("-q", "--query",
                        nargs="*",
                        dest="query",
                        help="""query the database. Options: [-q] [-q top #nr] [-q worst #nr] \n 
                                             [-q top_alb #nr] [-q worst_alb #nr] [-q top_art #nr #mt] 
                                             [-q hist] [-q evol] [-q codec] \n 
                                             [-q help] """ )

    parser.add_argument("-d", "--dr_database",
                        action="store_true",
                        dest="dr_database",
                        help="Output file compatible with the DR database at http:///www.dr.loudness-war.info")

    parser.add_argument("--hist",
                        action="store_true",
                        dest="histogram",
                        help="Plot the histogram of dynamic of a single file and exit")

    parser.add_argument("--lev_hist",
                        action="store_true",
                        dest="lev_histogram",
                        help="Plot the histogram of the saples levels of a single file and exit")

    parser.add_argument("--spectrogram",
                        action="store_true",
                        dest="spectrogram",
                        help="Plot the spectrogram of a single file and exit (beta)")

    parser.add_argument("--plot_track",
                        action="store_true",
                        dest="plot_track",
                        help="Plot the track of the given file and exit")

    parser.add_argument("--plot_track_dst",
                        action="store_true",
                        dest="plot_track_dst",
                        help="Plot the track in a cool manner of the given file and exit")

    parser.add_argument("--compress",
                        action="store",
                        choices=["very_soft", "v", "soft", "s",
                                 "medium", "m", "hard", "h", "very_hard", "vh"],
                        default=None,
                        dest="compress",
                        help="Perform the dynamic compression on a single file and exit, the resulting track will be written in a temp directory")

    parser.add_argument("--dyn_vivacity",
                        action="store_true",
                        dest="dynamic_vivacity",
                        help="Plot the graph of the dynamic vivacity of a single audio file and exit")

    parser.add_argument("--files_list",
                        action='store_true',
                        dest="files_list",
                        help="takes a files list and compute the DR of each file, if no files are specified, it reads from STDIN")

    parser.add_argument("--quiet",
                        action="store_true",
                        dest="quiet",
                        help="Quiet mode")

    parser.add_argument("--skip_version_check",
                        action="store_true",
                        dest="skip_version_check",
                        help="Do not check for new versions")

    parser.add_argument("-v", "--version",
                        action="store_true",
                        dest="version",
                        help="print the current version and exit")

    parser.add_argument("--tag", 
                        action="store_true",
                        dest="tag",
                        help="Write the DR to the tag of the input files")

    parser.add_argument(
        dest="path_name",
        nargs='?',
        default=None
    )

    return parser.parse_args()
