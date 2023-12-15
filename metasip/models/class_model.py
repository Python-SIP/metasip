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


from ..dip.model import Bool, Str

from .access_mixin import AccessMixin
from .code_model import CodeModel
from .code_container_mixin import CodeContainerMixin
from .docstring_mixin import DocstringMixin


class ClassModel(CodeModel, CodeContainerMixin, DocstringMixin, AccessMixin):
    """ This class implements a class. """

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

    # The optional %ConvertFromTypeCode.
    convfromtypecode = Str()

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

    # The optional %FinalisationCode.
    finalisationcode = Str()

    # The optional %TypeCode.
    typecode = Str()

    # The optional %TypeHeaderCode.
    typeheadercode = Str()

    # The optional %TypeHintCode.
    typehintcode = Str()
