# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


from dataclasses import dataclass, field
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from .code import Code


@dataclass
class CodeContainer:
    """ This class is a mixin for APIs that can contain other APIs. """

    # The list of contained API items.
    content: List['Code'] = field(default_factory=list)
