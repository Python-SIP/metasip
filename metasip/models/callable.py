# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


from dataclasses import dataclass, field
from typing import List

from .argument import Argument
from .code import Code


@dataclass
class Callable(Code):
    """ This class implements API items that represent most callables (i.e.
    everything except destructors).
    """

    # The C/C++ arguments.
    args: List[Argument] = field(default_factory=list)

    # The optional %MethodCode.
    methcode: str = ''

    # The name of the callable.
    name: str = ''

    # The optional Python arguments.
    pyargs: str = ''

    # The optional Python return type.
    pytype: str = ''

    # The C/C++ return type.  This is not used by constructors.
    rtype: str = ''
