# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


from dataclasses import dataclass

from .access import Access
from .code import Code


@dataclass
class Variable(Code, Access):
    """ This class implements C struct and C++ class member variables. """

    # The optional %AccessCode.
    accesscode: str = ''

    # The optional %GetCode.
    getcode: str = ''

    # The name of the variable.
    name: str = ''

    # The optional %SetCode.
    setcode: str = ''

    # This is set if the variable is static.
    static: bool = False

    # The type of the variable.
    type: str = ''
