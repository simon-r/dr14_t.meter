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

import os
import re
from setuptools import setup
from dr14tmeter.dr14_global import dr14_version

GITHUB = "https://github.com/simon-r/dr14_t.meter"

# PyPI cannot resolve relative links, so point them at the GitHub repository
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "README.md"), encoding="utf-8") as f:
    long_description = re.sub(r"\]\((?!https?://)([^)]+)\)", r"](%s/blob/master/\1)" % GITHUB, f.read())


setup(name = "DR14-T.meter",
    version = "%s" % dr14_version() ,
    description = "Compute the DR14 value of the given audio files",
    author = "Simone Riva",
    author_email = "simone.rva [at] gmail.com",
    url = GITHUB,
    project_urls = {
        "Source": GITHUB,
        "Bug Tracker": GITHUB + "/issues",
        "Documentation": GITHUB + "/blob/master/how_to_use.md",
    },
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
    long_description = long_description ,
    long_description_content_type = "text/markdown" ,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Topic :: Multimedia'] ,
)
