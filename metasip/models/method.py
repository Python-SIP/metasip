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

from .callable import Callable
from .docstring import Docstring
from .extended_access import ExtendedAccess


@dataclass
class Method(Callable, Docstring, ExtendedAccess):
    """ This class implements a C++ class method. """

    # This is set if the method is abstract.
    abstract: bool = False

    # This is set if the method is const.
    const: bool = False

    # This is set if the method is final.
    final: bool = False

    # This is set if the method is static.
    static: bool = False

    # The optional %VirtualCatcherCode.
    virtcode: str = ''

    # This is set if the method is virtual.
    virtual: bool = False
