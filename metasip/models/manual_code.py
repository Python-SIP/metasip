# Copyright (c) 2023 Riverbank Computing Limited.
#
# This file is part of metasip.
#
# This file may be used under the terms of the GNU General Public License v3
# as published by the Free Software Foundation which can be found in the file
# LICENSE-GPL3.txt included in this package.
#
# This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
# WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.


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
    # strin then this is copied to the .sip file unaltered.  If the body
    # attribute is not an empty string then this is copied to the .sip file as
    # a comment above the body.
    precis: str = ''
