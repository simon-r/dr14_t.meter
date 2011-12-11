from distutils.core import setup

#This is a list of files to install, and where
#(relative to the 'root' dir, where setup.py is)
#You could be more specific.
#iles = ["things/*"]

setup(name = "dr14_tmeter",
    version = "0.5.4",
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
