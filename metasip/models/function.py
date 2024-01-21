# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


from dataclasses import dataclass

from .callable import Callable
from .docstring import Docstring


@dataclass
class Function(Callable, Docstring):
    """ This class implements a global C/C++ function. """
