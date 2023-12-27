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


from dataclasses import dataclass

from .code_container import CodeContainer


@dataclass
class SipFile(CodeContainer):
    """ This class implements a .sip file. """

    # The optional %ExportedHeaderCode.
    exportedheadercode: str = ''

    # The optional %ExportedTypeHintCode.
    exportedtypehintcode: str = ''

    # The optional %InitialisationCode.
    initcode: str = ''

    # The optional %ModuleCode.
    modulecode: str = ''

    # The optional %ModuleHeaderCode.
    moduleheadercode: str = ''

    # The basename of the header file.  All header files that contribute to the
    # .sip file will have the same basename.  Note that there may not be any
    # record in the project of those contributing header files (or the
    # directories they were contained in).
    name: str = ''

    # The optional %PostInitialisationCode.
    postinitcode: str = ''

    # The optional %PreInitialisationCode.
    preinitcode: str = ''

    # The optional %TypeHintCode.
    typehintcode: str = ''
