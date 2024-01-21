# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


from dataclasses import dataclass

from .callable import Callable
from .docstring import Docstring
from .extended_access import ExtendedAccess


@dataclass
class Method(Callable, Docstring, ExtendedAccess):
    """ This class implements a C++ class method. """

    # This is set if the method is abstract.
    abstract: bool = False

    # This is set if the method is const.
    const: bool = False

    # This is set if the method is final.
    final: bool = False

    # This is set if the method is static.
    static: bool = False

    # The optional %VirtualCatcherCode.
    virtcode: str = ''

    # This is set if the method is virtual.
    virtual: bool = False
