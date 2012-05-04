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


from dip.model import Enum, Int, Str

from .i_code_container import ICodeContainer
from .i_version_range import IVersionRange
from .i_workflow import IWorkflow


class IHeaderFile(ICodeContainer, IVersionRange, IWorkflow):
    """ The IHeaderFile interface is implemented by models that represent a
    C/C++ .h file.
    """

    # The optional %ExportedHeaderCode.
    exportedheadercode = Str()

    # The identifier of the header file.
    id = Int()

    # The optional %InitialisationCode.
    initcode = Str()

    # The MD5 siganture of the header file excluding any initial comments.
    md5 = Str()

    # The optional %ModuleCode.
    modulecode = Str()

    # The optional %ModuleHeaderCode.
    moduleheadercode = Str()

    # The name of the header file.
    name = Str()

    # This specifies if the header file needs parsing.
    # FIXME: Change to Bool.
    parse = Enum('', 'needed')

    # The optional %PostInitialisationCode.
    postinitcode = Str()

    # The optional %PreInitialisationCode.
    preinitcode = Str()
