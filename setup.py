# dr14_t.meter: compute the DR14 value of the given audiofiles
#Copyright (C) 2011  Simone Riva
#
#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.


from distutils.core import setup
from dr14tmeter.dr14_global import dr14_version

#This is a list of files to install, and where
#(relative to the 'root' dir, where setup.py is)
#You could be more specific.
#iles = ["things/*"]

setup(name = "dr14_tmeter",
    version = "%s" % dr14_version() ,
    description = "Compute the DR14 value of the given audio files",
    author = "Simone Riva",
    author_email = "simone.rva [at] gmail.com",
    url = "http://simon-r.github.com/dr14_t.meter",
    #Name the folder where your packages live:
    #(If you have other packages (dirs) or modules (py files) then
    #put them into the package directory - they will be found 
    #recursively.)
    packages = ['dr14tmeter'],
    #'package' package must contain files (see list above)
    #I called the package 'package' thus cleverly confusing the whole issue...
    #This dict maps the package name =to=> directories
    #It says, package *needs* these files.
    #package_data = {'package' : files },
    #'runner' is in the root.
    scripts = ["dr14_tmeter"],
    long_description = "Compute the DR14 value of the given audio files according to the algorithm decribed by the Pleasurize Music Foundation" 
    #
    #This next part it for the Cheese Shop, look a little down the page.
    #classifiers = []     
) 
