# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


from dataclasses import dataclass


@dataclass
class VersionRange:
    """ This class implements a range of versions. """

    # The end version.
    endversion: str = ''

    # The start version.
    startversion: str = ''
