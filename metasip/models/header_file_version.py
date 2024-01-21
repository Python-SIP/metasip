# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


from dataclasses import dataclass


@dataclass
class HeaderFileVersion:
    """ This class implements a single version of a C/C++ .h file. """

    # The MD5 signature of the header file excluding any initial comments.
    md5: str = ''

    # This specifies if the header file needs parsing.
    parse: bool = False

    # The version of the header file.  This will be empty if the project does
    # not have any versions defined.
    version: str = ''
