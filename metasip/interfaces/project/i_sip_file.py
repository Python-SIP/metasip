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


from dip.model import Str

from .i_code_container import ICodeContainer


class ISipFile(ICodeContainer):
    """ The ISipFile interface is implemented by models that represent a .sip
    file.
    """

    # The optional %ExportedHeaderCode.
    exportedheadercode = Str()

    # The optional %InitialisationCode.
    initcode = Str()

    # The optional %ModuleCode.
    modulecode = Str()

    # The optional %ModuleHeaderCode.
    moduleheadercode = Str()

    # The basename of the header file.  All header files that contribute to the
    # .sip file will have the same basename.
    name = Str()

    # The optional %PostInitialisationCode.
    postinitcode = Str()

    # The optional %PreInitialisationCode.
    preinitcode = Str()
