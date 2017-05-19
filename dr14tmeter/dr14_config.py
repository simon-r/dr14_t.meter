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


import os.path
import os
import sys

if sys.version_info[0] == 2:
    import ConfigParser
else:
    import configparser as ConfigParser


def get_config_directory(create=True):

    p = os.environ.get('XDG_CONFIG_HOME')

    if p is None or not os.path.isabs(p):
        p = os.path.expanduser('~/.config')

    cfg_dir = os.path.join(p, 'dr14tmeter')

    if not os.path.isdir(cfg_dir) and create:
        os.mkdir(cfg_dir)

    return cfg_dir


def get_config_file(create=True):
    cfg_dir = get_config_directory()
    cfg_file = "%s/%s" % (cfg_dir, "dr14.cfg")

    if not os.path.isfile(cfg_file) and create:
        write_default_cfg(cfg_file)

    return cfg_file


def write_default_cfg(cfg_file):
    config = ConfigParser.ConfigParser()

    config.add_section('config_version')
    config.set('config_version', 'number', '1')

    config.add_section('database')

    config.set('database', 'enabled', 'False')
    config.set('database', 'path', get_config_directory() + "/dr14.db")
    config.set('database', 'collection_dir', '/')

    with open(cfg_file, 'w') as configfile:
        config.write(configfile)


def set_db_path(full_file_path):
    set_config_field('database', 'path', full_file_path)


def enable_db(flag=True):
    set_config_field('database', 'enabled', str(flag))


def database_exists():
    dbp = get_db_path()
    if os.path.isfile(dbp):
        return True
    else:
        return False


def set_collection_dir(path):
    set_config_field('database', 'collection_dir', path)


def set_config_field(section, field, value):
    cfg_file = get_config_file()
    config = ConfigParser.ConfigParser()
    config.read(cfg_file)
    config.set(section, field, value)
    with open(cfg_file, 'w') as configfile:
        config.write(configfile)


def get_db_path():
    return get_config_filed('database', 'path')


def db_is_enabled():
    s = get_config_filed('database', 'enabled')
    return s.lower() in ["yes", "true", "t", "1", "ok", "yup"]


def get_collection_dir():
    return get_config_filed('database', 'collection_dir')


def get_config_filed(section, field):
    config = ConfigParser.ConfigParser()
    cfg_file = get_config_file()
    config.read(cfg_file)
    return config.get(section, field)
