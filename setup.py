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


import sys

if sys.version_info < (3, 6):
    sys.exit("dr14_tmeter requires Python 3.6 or later, run: python3 -m pip install .")

from setuptools import setup
from dr14tmeter.dr14_global import dr14_version


setup(name = "dr14_tmeter",
    version = "%s" % dr14_version() ,
    description = "Compute the DR14 value of the given audio files",
    author = "Simone Riva",
    author_email = "simone.rva [at] gmail.com",
    url = "http://simon-r.github.com/dr14_t.meter",
    packages = ['dr14tmeter'],
    scripts = ["dr14_tmeter"],
    data_files = [('share/man/man1', ['man/dr14_tmeter.1'])],
    python_requires = ">=3.6",
    install_requires = ['numpy'],
    extras_require = {
        'plot': ['matplotlib'],
        'compress': ['scipy'],
        'tag': ['mutagen'],
    },
    long_description = "Compute the DR14 value of the given audio files according to the algorithm decribed by the Pleasurize Music Foundation" ,
    classifiers=[
        'Development Status :: %s Stable' % dr14_version() ,
        'Environment :: Console',
        'Intended Audience :: Users',
        'License :: OSI Approved :: GPL-3.0+',
        'Operating System :: Linux',
        'Programming Language :: Python',
        'Topic :: Multimedia'] ,
)
