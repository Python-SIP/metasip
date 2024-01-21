# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


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
