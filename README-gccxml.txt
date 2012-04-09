Notes for Installing GCC-XML
============================

Installing cmake
----------------

OS/X
....

Download the installer image from::

    http://cmake.org/cmake/resources/software.html

Install the package, including the command line symlinks.


Getting the GCC-XML Source
--------------------------

    cvs -d :pserver:anoncvs@www.gccxml.org:/cvsroot/GCC_XML login
    cvs -d :pserver:anoncvs@www.gccxml.org:/cvsroot/GCC_XML co gccxml

The password is blank.


Building GCC-XML
----------------

Run the following commands::

    mkdir /path/to/build/dir
    cd /path/to/build/dir
    cmake /path/to/src/gccxml
    make
    sudo make install
