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


from dip.model import Bool, Str

from .i_annos import IAnnos


class IArgument(IAnnos):
    """ The IArgument interface is implemented by models representing an
    argument of a callable.
    """

    # The optional default value of the argument.  This is interpreted
    # literally so that (for example) a string value includes the quotes.
    default = Str()

    # The optional name of the argument.
    name = Str()

    # The optional Python type of the argument.
    pytype = Str()

    # The C/C++ type of the argument.
    type = Str()

    # This is set if the name of the argument hasn't been verified, i.e.
    # accepted for use (typically as a keyword argument).
    unnamed = Bool(True)
