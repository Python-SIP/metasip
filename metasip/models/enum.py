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

from .access import Access
from .code import Code
from .enum_value import EnumValue


@dataclass
class Enum(Code, Access):
    """ This class implements an enum. """

    # The list of enum values.
    content: list[EnumValueModel] = field(default_factory=list)

    # Set if the enum is a C++11 enum class.
    enum_class: bool = False

    # The optional name of the enum.
    name: str = ''
