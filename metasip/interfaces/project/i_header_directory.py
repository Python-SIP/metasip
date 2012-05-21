# Copyright (c) 2012 Riverbank Computing Limited.
#
# This file is part of metasip.
#
# This file may be used under the terms of the GNU General Public License v3
# as published by the Free Software Foundation which can be found in the file
# LICENSE-GPL3.txt included in this package.
#
# This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
# WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.


from dip.model import Interface, List, Str

from .i_header_file import IHeaderFile


class IHeaderDirectory(Interface):
    """ The IHeaderDirectory interface is implemented by models that represent
    a directory containing C/C++ .h files.
    """

    # The list of C/C++ .h files in the directory.
    content = List(IHeaderFile)

    # The optional glob-like filter to apply to file names.
    filefilter = Str()

    # The suffix added to the input dirextory to create the full name of the
    # directory.
    inputdirsuffix = Str()

    # The name of the header directory.  This is used for display purposes.
    name = Str()

    # The optional additional arguments passed to the external C++ parser.
    parserargs = Str()

    # The versions for which the header directory needs scanning.  A single
    # empty string means that no explicit versions have been defined but the
    # header directory needs scanning.
    scan = List(Str())
