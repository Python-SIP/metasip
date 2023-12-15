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


from ..dip.model import Str

from .code_container_mixin import CodeContainerMixin


class SipFileModel(CodeContainerMixin):
    """ This class implements a .sip file. """

    # The optional %ExportedHeaderCode.
    exportedheadercode = Str()

    # The optional %ExportedTypeHintCode.
    exportedtypehintcode = Str()

    # The optional %InitialisationCode.
    initcode = Str()

    # The optional %ModuleCode.
    modulecode = Str()

    # The optional %ModuleHeaderCode.
    moduleheadercode = Str()

    # The optional %TypeHintCode.
    typehintcode = Str()

    # The basename of the header file.  All header files that contribute to the
    # .sip file will have the same basename.  Note that there may not be any
    # record in the project of those contributing header files (or the
    # directories they were contained in).
    name = Str()

    # The optional %PostInitialisationCode.
    postinitcode = Str()

    # The optional %PreInitialisationCode.
    preinitcode = Str()
