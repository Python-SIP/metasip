# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


from dataclasses import dataclass

from .access import Access
from .callable import Callable
from .docstring import Docstring


@dataclass
class Constructor(Callable, Docstring, Access):
    """ This class implements a C++ constructor. """

    # This is set if the constructor is explicit.
    explicit: bool = False
