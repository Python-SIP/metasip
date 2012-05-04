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
    """ The IClass interface is implemented by models representing a class. """

    # The C++ base classes.
    bases = Str()

    # The optional %BIGetCharBufferCode.
    bicharbufcode = Str()

    # The optional %BIGetBufferCode.
    bigetbufcode = Str()

    # The optional %BIReadBufferCode.
    bireadbufcode = Str()

    # The optional %BIReleaseBufferCode.
    birelbufcode = Str()

    # The optional %BIGetSegCountCode.
    bisegcountcode = Str()

    # The optional %BIWriteBufferCode.
    biwritebufcode = Str()

    # The optional %ConvertToTypeCode.
    convtotypecode = Str()

    # The optional %GCClearCode.
    gcclearcode = Str()

    # The optional %GCTraverseCode.
    gctraversecode = Str()

    # The name of the class.
    name = Str()

    # The optional %PickleCode.
    picklecode = Str()

    # The optional Python base classes.  An empty string means that the C++
    # base classes should be used.  A value of "None" means that there are no
    # base classes.
    pybases = Str()

    # This is set if the class is a struct.
    struct = Bool(False)

    # The optional %ConvertToSubClassCode.
    subclasscode = Str()

    # The optional %TypeCode.
    typecode = Str()

    # The optional %TypeHeaderCode.
    typeheadercode = Str()
