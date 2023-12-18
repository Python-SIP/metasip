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


@dataclass
class CodeContainer:
    """ This class is a mixin for APIs that can contain other APIs. """

    # The list of contained API items.
    content: list['.code.Code'] = field(default_factory=list)
