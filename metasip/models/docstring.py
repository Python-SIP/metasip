# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


from dataclasses import dataclass


@dataclass
class Docstring:
    """ This class is a mixin for APIs that can have a docstring. """

    # The optional doc string.
    docstring: str = ''
