# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


from dataclasses import dataclass

from .access import Access
from .code import Code


@dataclass
class Destructor(Code, Access):
    """ This class implements a C++ destructor. """

    # The optional %MethodCode.
    methcode: str = ''

    # The name of the destructor (ie. the class).
    name: str = ''

    # The optional %VirtualCatcherCode.
    virtcode: str = ''

    # This is set if the destructor is virtual.
    virtual: bool = False
