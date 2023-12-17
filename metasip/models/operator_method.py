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
from .callable import Callable


@dataclass
class OperatorMethod(Callable, Access):
    """ This class implements a C++ class operator. """

    # This is set if the operator is abstract.
    abstract: bool = False

    # This is set if the operator is const.
    const: bool = False

    # The optional %VirtualCatcherCode.
    virtcode: str = ''

    # This is set if the operator is virtual.
    virtual: bool = False
