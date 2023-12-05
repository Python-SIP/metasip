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


from ...dip.model import Bool, Interface, Str


class IHeaderFileVersion(Interface):
    """ The IHeaderFileVersion interface is implemented by models that
    represent a single version of a C/C++ .h file.
    """

    # The MD5 signature of the header file excluding any initial comments.
    md5 = Str()

    # This specifies if the header file needs parsing.
    parse = Bool(True)

    # The version of the header file.  This will be empty if the project does
    # not have any versions defined.
    version = Str()
