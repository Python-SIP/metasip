# Copyright (c) 2023 Riverbank Computing Limited.
#
# This file is part of metasip.
#
# This file may be used under the terms of the GNU General Public License v3
# as published by the Free Software Foundation which can be found in the file
# LICENSE-GPL3.txt included in this package.
#
# This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
# WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.


from dataclasses import dataclass, field

from .header_file import HeaderFile


@dataclass
class HeaderDirectory:
    """ This class implements a directory containing C/C++ .h files. """

    # The list of C/C++ .h files in the directory.
    content: list[HeaderFile] = field(default_factory=list)

    # The optional glob-like filter to apply to file names.
    filefilter: str = ''

    # The suffix added to the input directory to create the full name of the
    # directory.
    # TODO: the way this is currently used it is platform-specific and needs to
    # be platform neutral.  It is also poorly named - it is the sub-path
    # relative to the source directory of the header directory.
    inputdirsuffix: str = ''

    # The name of the header directory.  This is used for display purposes.
    name: str = ''

    # The optional additional arguments passed to the external C++ parser.
    parserargs: str = ''

    # The versions for which the header directory needs scanning.  A single
    # empty string means that no explicit versions have been defined but the
    # header directory needs scanning.
    scan: list[str] = field(default_factory=list)
