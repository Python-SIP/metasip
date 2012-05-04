# Copyright (c) 2012 Riverbank Computing Limited.
#
# This file is part of metasip.
#
# This file may be used under the terms of the GNU General Public License v3
# as published by the Free Software Foundation which can be found in the file
# LICENSE-GPL3.txt included in this package.
#
# This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
# WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.


from dip.model import List, Str

from .i_argument import IArgument
from .i_code import ICode


class ICallable(ICode):
    """ The ICallable interface is implemented by API items that represent
    most callables (i.e. everything except destructors).
    """

    # The C/C++ arguments.
    args = List(IArgument)

    # The optional %MethodCode.
    methcode = Str()

    # The name of the callable.
    # FIXME: Don't use for constructors or add a new interface that excludes
    #        name, pytype and rtype.
    name = Str()

    # The optional Python arguments.
    pyargs = Str()

    # The optional Python return type.
    pytype = Str()

    # The C/C++ return type.  This is not used by constructors.
    rtype = Str()
