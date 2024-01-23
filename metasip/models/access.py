# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


from dataclasses import dataclass


@dataclass
class Access:
    """ This class is a mixin for API models subject to standard C++ access
    specifiers.
    """

    # The access specifier.  Values are '' (meaning public), 'protected' and
    # 'private'.
    access: str = ''
