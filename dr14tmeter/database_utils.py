
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

from dr14tmeter.database import dr_database_singletone
from dr14tmeter.table import *
from dr14tmeter.audio_analysis import *
from dr14tmeter.dr14_global import *
from dr14tmeter.dr14_config import *
from dr14tmeter.write_dr import WriteDr, WriteDrExtended
from dr14tmeter.query import *
from dr14tmeter.out_messages import *

import subprocess
import sys
import re


def local_dr_database_configure():

    subprocess.call("clear", shell=True)

    print_out(
        "---------------------------------------------------------------------------------------------- ")
    print_out("- DR14 T.meter --  ")
    print_out("- Local DR database - Configuration procedure ")
    print_out(
        "---------------------------------------------------------------------------------------------- ")

    print_out("  ")
    print_out(
        "  The database, if enabled, automatically stores all DR result in a local database ")
    print_out("  - You must set up some parameters to use the database -")
    print_out("  ")

    flag = True
    while flag:
        print_out("  1. Insert the database directory: Default [%s]:" % os.path.split(
            get_db_path())[0])

        if sys.version_info[0] == 2:
            db_path = raw_input("     > ")
        else:
            db_path = input("     > ")

        db_path = os.path.expanduser(db_path)
        db_path = os.path.expandvars(db_path)

        if re.sub("\s+", "", db_path) == "":
            flag = False
            db_path = os.path.split(get_db_path())[0]
            continue

        db_path = os.path.abspath(db_path)

        if test_path_validity(db_path):
            flag = False
        else:
            print_out(
                "  - [ %s ] is not a directory, please insert an acceptable directory name" % db_path)

    print_out("  ")
    print_out(
        "---------------------------------------------------------------------------------------------- ")
    print_out("  ")
    print_out(
        "     If you set a collection directory ONLY the tracks inside this base folder and sub-folders ")
    print_out("     will be added to the database.")
    print_out(
        "     If you insert \'any\' all analyzed tracks will be added to the database ")

    flag = True
    while flag:
        print_out(
            "  2. Insert your collection directory: Dafault [%s] " % "any")

        if sys.version_info[0] == 2:
            coll_path = raw_input("     > ")
        else:
            coll_path = input("     > ")

        coll_path = os.path.expanduser(coll_path)
        coll_path = os.path.expandvars(coll_path)

        if re.sub("(\s+)", "", coll_path) in ["", "any"]:
            flag = False
            coll_path = "/"
            continue

        coll_path = os.path.abspath(coll_path)

        if os.path.isdir(coll_path):
            flag = False
        else:
            print_out(
                "  - [ %s ] is not a directory, please insert an existing directory name" % coll_path)

    print_out("  ")
    print_out(" type: %s -q " % get_exe_name())
    print_out(" For more details and querying the database ")
    print_out(
        "---------------------------------------------------------------------------------------------- ")

    return (db_path, coll_path)


def fix_problematic_database():

    print_out("  ")
    print_out(" It likes that your database have some problems ")
    print_out("  ")
    print_out(" Options: ")
    print_out("   1. Rebuild the database and back-up the damaged db")
    print_out("   2. Disable the database ")
    print_out("  ")
    nr = input_number(p=" > ", rng=(1, 2))

    dbp = get_db_path()

    if nr == 1:
        if os.path.isfile(dbp):
            dest_file = dbp + ".d_save"
            os.rename(dbp, dest_file)
            print_out("  ")
            print_out(
                " The old database has been saved in the file: %s " % dest_file)
            print_out("  ")

        enable_database(prompt=False)

    elif nr == 2:
        enable_db(False)
        print_out(" The database has been disabled ")
        print_out(" Type: %s --enable_database " % get_exe_name())
        print_out(" For enabling the database ")
        print_out("  ")


def enable_database(prompt=True):

    f = False

    if database_exists() and db_is_enabled():
        f = True

    if database_exists() and not db_is_enabled():
        db = dr_database_singletone().get()
        f = db.is_db_valid()

        if not f:
            dbp = get_db_path()
            dest_file = dbp + ".de_save"
            os.rename(dbp, dest_file)
        else:
            f = True

    if not database_exists():

        if prompt:
            (db_path, coll_dir) = local_dr_database_configure()
        else:
            db_path = os.path.split(get_db_path())[0]
            coll_dir = get_collection_dir()

        try:
            os.makedirs(db_path)
        except:
            pass

        db_path += "/dr14_database.db"

        set_db_path(db_path)
        set_collection_dir(coll_dir)

        print_msg("Preparing database .... ")
        db = dr_database_singletone().get()
        db.build_database()
        f = db.is_db_valid()

    if f:
        enable_db(True)
        print_msg(
            "The local DR database is ready and enabled! It is located in the file: %s  " % get_db_path())
    else:
        print_err("The building procedure of the database has failed ... retry ")
    return


def input_number(p=" > ", rng=(0, 2**31)):

    flag = True

    while flag:
        if sys.version_info[0] == 2:
            nr = raw_input(" > ")
        else:
            nr = input(" > ")

        try:
            nr = int(nr)
        except:
            print_out(" !! Please insert a valid number ")
            continue

        if rng is not None and not (nr >= rng[0] and nr <= rng[1]):
            print_out(" !! Please insert a valid option number in the [%d .. %d]" % (
                min(rng), max(rng)))
            continue

        flag = False

    return nr


def extended_options(opt_nr):

    qa = False
    qb = False

    if opt_nr in [1, 2, 3, 5, 6]:
        question_a = "Insert the number of desired results: "
        qa = True

    if opt_nr in [3]:
        question_b = "Insert the minimal number of tracks required for inserting an artist in the result: "
        qb = True

    res = []

    if qa:
        print_out(question_a)
        res.append(input_number())

    if qb:
        print_out(question_b)
        res.append(input_number())

    return res


def query_helper():
    subprocess.call("clear", shell=True)
    print_out("----- QUERY HELPER -----")
    print_out("  ")
    print_out(" Choose one of the following query: ")
    print_out("  ")
    print_out(" 1. The list of the best DR tracks ")
    print_out(" 2. The list of the best DR Albums ")
    print_out(" 3. The list of the best DR Artists ")
    print_out(" 4. The DR time evolution, according with your collection")
    print_out(" 5. The list of the worst DR tracks  ")
    print_out(" 6. The list of the worst DR albums ")
    print_out(" 7. The DR histogram ")
    print_out(" 8. Used audio CODEC and mean DR ")
    print_out(" 0. Exit ")
    print_out("  ")

    nr = input_number(rng=(0, 9))

    class options:
        pass

    ext_opt = []

    if nr in [1, 2, 3, 5, 6]:
        print_out(
            " Do you want to set the query extended options? [N/y] (default: No)")
        if sys.version_info[0] == 2:
            an = raw_input(" > ")
        else:
            an = input(" > ")

        if an.lower() in ["y", "yes"]:
            ext_opt = extended_options(nr)

    if nr == 0:
        return
    elif nr == 1:
        options.query = ["top"]
    elif nr == 2:
        options.query = ["top_alb"]
    elif nr == 3:
        options.query = ["top_art"]
    elif nr == 4:
        options.query = ["evol"]
    elif nr == 5:
        options.query = ["worst"]
    elif nr == 6:
        options.query = ["worst_alb"]
    elif nr == 7:
        options.query = ["hist"]
    elif nr == 8:
        options.query = ["codec"]

    for e in ext_opt:
        options.query.append(e)

    eq_cmd = "%s -q " % get_exe_name()
    for o in options.query:
        eq_cmd += "%s " % o

    print_out("")
    print_out("equivalent command line:\n>    %s " % eq_cmd)
    print_out("")

    res = database_exec_query(options, tm=ExtendedTextTable())

    print_out("")
    print_out(res)


def database_exec_query(options, tm=ExtendedTextTable()):

    if len(options.query) >= 2:
        limit = int(options.query[1])
    else:
        limit = 30

    if len(options.query) >= 3:
        second_opt = options.query[2]
    else:
        second_opt = None

    if options.query[0] == "help":
        query_helper()
        return

    elif options.query[0] == "top":
        table_title = "Top DR tracks"
        q = query_top_dr()

    elif options.query[0] == "top_alb":
        table_title = "Top DR Albums"
        q = query_top_albums_dr()

    elif options.query[0] == "worst":
        table_title = "Worst DR Tracks"
        q = query_worst_dr()

    elif options.query[0] == "worst_alb":
        table_title = "Worst DR Albums"
        q = query_worst_albums_dr()

    elif options.query[0] == "top_art":
        table_title = "Top Artists"
        q = query_top_artists()
        if second_opt is not None:
            q.min_track = int(second_opt)

    elif options.query[0] == "hist":
        table_title = "DR histogram"
        q = query_dr_histogram()

    elif options.query[0] == "evol":
        table_title = "DR evolution"
        q = query_date_dr_evolution()

    elif options.query[0] == "codec":
        table_title = "Codec Info"
        q = query_dr_codec()

    else:
        raise Exception("Option not allowed")

    q.limit = limit

    wr = WriteDr()
    table_code = wr.write_query_result(
        q.exec_query(), tm, table_title, q.get_col_keys())

    return table_code
