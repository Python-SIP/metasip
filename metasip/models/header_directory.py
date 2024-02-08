# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


from dataclasses import dataclass, field
from typing import List

from .header_file import HeaderFile
from .platform import Platform


@dataclass
class HeaderDirectory:
    """ This class implements a directory containing C/C++ .h files. """

    # The list of C/C++ .h files in the directory.
    content: List[HeaderFile] = field(default_factory=list)

    # The platform-specific configurations.
    platforms: List[Platform] = field(default_factory=list)

    # The name of the header directory.  This is used for display purposes.
    name: str = ''

    # The versions for which the header directory needs scanning.  A single
    # empty string means that no explicit versions have been defined but the
    # header directory needs scanning.
    scan: List[str] = field(default_factory=list)
