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

from .header_file_version import HeaderFileVersion


@dataclass
class HeaderFile:
    """ This class implements a C/C++ .h file. """

    # This is set if the header file is being ignored, i.e. it will never be
    # assigned to a module.
    ignored: bool = False

    # The name of the optional module that the header file is assigned to.
    module: str = ''

    # The basename of the header file.
    name: str = ''

    # The individual versions of the header file.  The list will be empty if
    # it is being ignored.  If no versions have been defined the the list will
    # have one element.  Note that these are unordered.
    versions: list[HeaderFileVersion] = field(default_factory=list)
