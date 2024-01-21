# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


from dataclasses import dataclass

from .annos import Annos


@dataclass
class Argument(Annos):
    """ This class implements an argument of a callable. """

    # The optional C/C++ default value of the argument.  This is interpreted
    # literally so that (for example) a string value includes the quotes.
    default: str = ''

    # The optional name of the argument.
    name: str = ''

    # The optional Python default value of the argument.
    pydefault: str = ''

    # The optional Python type of the argument.
    pytype: str = ''

    # The C/C++ type of the argument.
    type: str = ''

    # This is set if the name of the argument hasn't been verified, i.e.
    # accepted for use (typically as a keyword argument).
    unnamed: bool = True
