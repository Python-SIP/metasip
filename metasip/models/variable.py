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

from .access import Access
from .code import Code


@dataclass
class Variable(Code, Access):
    """ This class implements C struct and C++ class member variables. """

    # The optional %AccessCode.
    accesscode: str = ''

    # The optional %GetCode.
    getcode: str = ''

    # The name of the variable.
    name: str = ''

    # The optional %SetCode.
    setcode: str = ''

    # This is set if the variable is static.
    static: bool = False

    # The type of the variable.
    type: str = ''
