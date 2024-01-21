# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


from dataclasses import dataclass

from .code import Code


@dataclass
class Typedef(Code):
    """ This class implements a typedef. """

    # The name of the type.
    name: str = ''

    # The definition of the type.
    type: str = ''
