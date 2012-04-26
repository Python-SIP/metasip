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


from dip.model import Bool, Str

from .i_access import IAccess
from .i_code import ICode
from .i_code_container import ICodeContainer
from .i_doc_string import IDocString


class IClass(ICode, ICodeContainer, IDocString, IAccess):

    bases = Str()

    bicharbufcode = Str()

    bigetbufcode = Str()

    bireadbufcode = Str()

    birelbufcode = Str()

    bisegcountcode = Str()

    biwritebufcode = Str()

    convtotypecode = Str()

    gcclearcode = Str()

    gctraversecode = Str()

    name = Str()

    picklecode = Str()

    pybases = Str()

    struct = Bool(False)

    subclasscode = Str()

    typecode = Str()

    typeheadercode = Str()
