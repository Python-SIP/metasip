# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


from dataclasses import dataclass

from .access import Access
from .callable import Callable


@dataclass
class OperatorMethod(Callable, Access):
    """ This class implements a C++ class operator. """

    # This is set if the operator is abstract.
    abstract: bool = False

    # This is set if the operator is const.
    const: bool = False

    # The optional %VirtualCatcherCode.
    virtcode: str = ''

    # This is set if the operator is virtual.
    virtual: bool = False
