Notes for Installing GCC-XML
============================

Installing cmake
----------------

OS/X
....

Download the installer image from::

    http://cmake.org/cmake/resources/software.html

Install the package, including the command line symlinks.

GCC-XML appears to have a bug where the preprocessor tries to evaluate all
parts of a logical and (ie. &&) expression rather than stopping with the first
part that evaluates to 0.  This breaks some OS/X and Qt v5 header files.  To
fix these:

- edit limits.h and stdint.h in the
  /Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/lib/clang/5.0/include
  directory and add::

    #if defined(__GCCXML__)
    #define __has_include_next(x)   (0)
    #endif

- edit ~/usr/qt-5/include/QtCore/qcompilerdetection.h and stddef.h in the
  /Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/lib/clang/5.0/include
  directory and add::

    #if defined(__GCCXML__)
    #define __has_feature(x)    (0)
    #endif

- edit __config in the
  /Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/lib/c++/v1
  directory and add::

    #if defined(__GCCXML__)
    #undef __clang__
    #define __has_attribute(x)  (0)
    #endif

- edit ~/usr/qt-5/include/QtCore/qisenum.h and add::

    #if defined(__GCCXML__)
    #define __has_extension(x)  (0)
    #endif


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
