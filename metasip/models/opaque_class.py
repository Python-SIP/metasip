# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


from dataclasses import dataclass

from .access import Access
from .code import Code


@dataclass
class OpaqueClass(Code, Access):
    """ This class implements an opaque class. """

    # The name of the class.
    name: str = ''
