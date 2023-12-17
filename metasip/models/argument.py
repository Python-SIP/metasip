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
