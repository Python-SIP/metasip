# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


from dataclasses import dataclass, field
from typing import List

from .access import Access
from .code import Code
from .enum_value import EnumValue


@dataclass
class Enum(Code, Access):
    """ This class implements an enum. """

    # The list of enum values.
    content: List[EnumValue] = field(default_factory=list)

    # Set if the enum is a C++11 enum class.
    enumclass: bool = False

    # The optional name of the enum.
    name: str = ''
