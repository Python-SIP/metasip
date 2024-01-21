# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


from dataclasses import dataclass

from .callable import Callable


@dataclass
class OperatorFunction(Callable):
    """ This class implements a global C++ operator. """
