# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


from dataclasses import dataclass


@dataclass
class Platform:
    """ This class implements a header directory and platform specific
    configuration.
    """

    # The suffix added to the input directory to create the glob pattern that
    # defines the input files.
    inputdirpattern: str = ''

    # The name of the platform.  This is used for display purposes.
    name: str = ''

    # The optional additional arguments passed to the external C++ parser.
    parserargs: str = ''
