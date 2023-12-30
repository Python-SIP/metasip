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


from dataclasses import dataclass, field

from .argument import Argument
from .code import Code


# TODO: add ClassCallable to deal with 'virt', 'virtcode', 'const'? 'abstract'?
@dataclass
class Callable(Code):
    """ This class implements API items that represent most callables (i.e.
    everything except destructors).
    """

    # The C/C++ arguments.
    args: list[Argument] = field(default_factory=list)

    # The optional %MethodCode.
    methcode: str = ''

    # The name of the callable.
    name: str = ''

    # The optional Python arguments.
    pyargs: str = ''

    # The optional Python return type.
    pytype: str = ''

    # The C/C++ return type.  This is not used by constructors.
    rtype: str = ''
