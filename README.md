# MetaSIP - a GUI Development Tool for SIP


[SIP](https://pypi.org/project/sip/) is a Python bindings generator for C and
C++ libraries.  It takes as its input a set of `.sip` text files that describes
the history of the API of the library.  A `.sip` file is similar to a C/C++
header file but with addional directives, annotations and supplementary
hand-written C/C++ code.

MetaSIP (specifically the `msip` application) is a GUI tool for specifying the
complete history of a library's API allowing additional directives, annotations
and hand-written code to be added.  A `.msp` project file is used to store this
information and MetaSIP (specifically the `msipgen` application) can generate
an appropriate set of `.sip` files to feed to SIP.

The key feature of MetaSIP is that it can scan the header files of a particular
version of a library in order to initially populate the project file.  It will
then indicate all of the tasks that might need to be performed in order to
complete the implementation of the bindings.  It will also scan a new version
of the library, compare it with the previous version, update the project file
appropriately, and indicate any new tasks that now might need to be performed
in order to keep the bindings up to date.  These features make it relatively
easy to maintain the bindings for a large library.

Currently the scanning of a library's header files is done using
[CastXML](https://github.com/CastXML/CastXML) and this must also be installed.

MetaSIP is implemented with Python and
[PyQt6](https://pypi.org/project/PyQt6/).

It should be noted that MetaSIP was developed a number of years ago by the
author as a personal productivity tool.  As a result it is fairly feature
complete.  However because it has not been used by a significant number of
people, its behavour may seem quirky in places.  It is certainly poorly
documented with no online help.


## Documentation

The documentation can be found at
[Read the Docs](https://metasip.readthedocs.io).


## License

MetaSIP is licensed under the BSD 2 clause license.


## Installation

To install `msipgen`, run:

    pip install metasip

To install the additional dependencies required by the `msip` GUI development
tool, run:

    pip install 'metasip[gui]'


## Creating Packages for Distribution

Python sdists and wheels can be created with any standard Python build
frontend.

For example, using [build](https://pypi.org/project/build/) an sdist and wheel
will be created from a checkout in the current directory by running:

    python -m build --outdir .


## Building the Documentation

The documentation is built using [Sphinx](https://pypi.org/project/Sphinx/),
[myst_parser](https://pypi.org/project/myst-parser/) and the
[sphinx-rtd-theme](https://pypi.org/project/sphinx-rtd-theme/) theme.

Change to the `docs` directory of a checkout and run:

    make html

The HTML documentation can then be found in the `_build/html` subdirectory.
