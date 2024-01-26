# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


from dataclasses import dataclass

from .code import Code
from .docstring import Docstring
from .extended_access import ExtendedAccess


@dataclass
class ManualCode(Code, Docstring, ExtendedAccess):
    """ This class implements an explicitly written API. """

    # The optional explicitly written API item.  If the API item can be
    # specified in a single line then the precis attribute is normally used
    # instead.
    body: str = ''

    # The optional %MethodCode.  This would not normally be specified if the
    # body attribute is not an empty string.
    methcode: str = ''

    # The one-line summary of the code.  If the body attribute is an empty
    # string then this is copied to the .sip file unaltered.  If the body
    # attribute is not an empty string then this is copied to the .sip file as
    # a comment above the body.
    precis: str = ''
