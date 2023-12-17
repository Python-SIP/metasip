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
class Destructor(Code, Access):
    """ This class implements a C++ destructor. """

    # The optional %MethodCode.
    methcode: str = ''

    # The name of the destructor.
    # FIXME: Remove this.
    name: str = ''

    # The optional %VirtualCatcherCode.
    virtcode: str = ''

    # This is set if the destructor is virtual.
    virtual: bool = False
