# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


from dataclasses import dataclass, field
from typing import List

from .header_file_version import HeaderFileVersion


@dataclass
class HeaderFile:
    """ This class implements a C/C++ .h file. """

    # This is set if the header file is being ignored, i.e. it will never be
    # assigned to a module.
    ignored: bool = False

    # The name of the optional module that the header file is assigned to.
    module: str = ''

    # The basename of the header file.
    name: str = ''

    # The individual versions of the header file.  The list will be empty if
    # it is being ignored.  If no versions have been defined the the list will
    # have one element.  Note that these are unordered.
    versions: List[HeaderFileVersion] = field(default_factory=list)
