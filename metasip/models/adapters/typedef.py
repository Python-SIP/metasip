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


from ..code import Code

from .adapt import adapt
from .base_adapter import AttributeType, BaseAdapter


class TypedefAdapter(BaseAdapter):
    """ This is the Typedef adapter. """

    # The map of attribute names and types.
    ATTRIBUTE_TYPE_MAP = {
        'name': AttributeType.STRING,
        'type': AttributeType.STRING,
    }

    def load(self, element, ui):
        """ Load the model from the XML element.  An optional user interface
        may be available to inform the user of progress.
        """

        super().load(element, ui)

        adapt(self.model, Code).load(element, ui)