# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


from dataclasses import dataclass, field


@dataclass
class CodeContainer:
    """ This class is a mixin for APIs that can contain other APIs. """

    # The list of contained API items.
    content: list['.code.Code'] = field(default_factory=list)
