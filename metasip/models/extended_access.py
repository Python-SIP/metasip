# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


from dataclasses import dataclass


@dataclass
class ExtendedAccess:
    """ This class is a mixin for APIs subject to the extended (i.e. Qt
    specific) C++ access specifiers.
    """

    # The access specifier.  Values are '' (meaning public), 'protected',
    # 'protected slots', 'private', 'public slots', 'signals'.
    access: str = ''
