# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


from dataclasses import dataclass

from .access import Access
from .callable import Callable


@dataclass
class OperatorCast(Callable, Access):
    """ This class implements a cast operator. """

    # This is set if the operator is const.
    const: bool = False
