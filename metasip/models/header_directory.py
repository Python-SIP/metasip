# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


from dataclasses import dataclass, field

from .header_file import HeaderFile


@dataclass
class HeaderDirectory:
    """ This class implements a directory containing C/C++ .h files. """

    # The list of C/C++ .h files in the directory.
    content: list[HeaderFile] = field(default_factory=list)

    # The optional glob-like filter to apply to file names.
    filefilter: str = ''

    # The suffix added to the input directory to create the full name of the
    # directory.
    inputdirsuffix: str = ''

    # The name of the header directory.  This is used for display purposes.
    name: str = ''

    # The optional additional arguments passed to the external C++ parser.
    parserargs: str = ''

    # The versions for which the header directory needs scanning.  A single
    # empty string means that no explicit versions have been defined but the
    # header directory needs scanning.
    scan: list[str] = field(default_factory=list)
