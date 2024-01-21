# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


from dataclasses import dataclass

from .access import Access
from .code import Code
from .code_container import CodeContainer
from .docstring import Docstring


@dataclass
class Class(Code, CodeContainer, Docstring, Access):
    """ This class implements a class. """

    # The C++ base classes.
    bases: str = ''

    # The optional %BIGetCharBufferCode (deprecated).
    bicharbufcode: str = ''

    # The optional %BIGetBufferCode.
    bigetbufcode: str = ''

    # The optional %BIReadBufferCode (deprecated).
    bireadbufcode: str = ''

    # The optional %BIReleaseBufferCode.
    birelbufcode: str = ''

    # The optional %BIGetSegCountCode (deprecated).
    bisegcountcode: str = ''

    # The optional %BIWriteBufferCode (deprecated).
    biwritebufcode: str = ''

    # The optional %ConvertFromTypeCode.
    convfromtypecode: str = ''

    # The optional %ConvertToTypeCode.
    convtotypecode: str = ''

    # The optional %GCClearCode.
    gcclearcode: str = ''

    # The optional %GCTraverseCode.
    gctraversecode: str = ''

    # The name of the class.
    name: str = ''

    # The optional %PickleCode.
    picklecode: str = ''

    # The optional Python base classes.  An empty string means that the C++
    # base classes should be used.  A value of "None" means that there are no
    # base classes.
    pybases: str = ''

    # This is set if the class is a struct.
    struct: bool = False

    # The optional %ConvertToSubClassCode.
    subclasscode: str = ''

    # The optional %FinalisationCode.
    finalisationcode: str = ''

    # The optional %TypeCode.
    typecode: str = ''

    # The optional %TypeHeaderCode.
    typeheadercode: str = ''

    # The optional %TypeHintCode.
    typehintcode: str = ''
