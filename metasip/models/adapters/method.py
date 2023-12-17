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


from ..callable import Callable
from ..docstring import Docstring
from ..extended_access import ExtendedAccess

from .adapt import adapt
from .base_adapter import AttributeType, BaseAdapter


class MethodAdapter(BaseAdapter):
    """ This is the Method adapter. """

    ATTRIBUTE_TYPE_MAP = {
        'abstract': AttributeType.BOOL_FALSE,
        'const':    AttributeType.BOOL_FALSE,
        'final':    AttributeType.BOOL_FALSE,
        'static':   AttributeType.BOOL_FALSE,
        'virtual':  AttributeType.BOOL_FALSE,
    }

    def load(self, element, ui):
        """ Load the model from the XML element.  An optional user interface
        may be available to inform the user of progress.
        """

        super().load(element, ui)

        adapt(self.model, Callable).load(element, ui)
        adapt(self.model, Docstring).load(element, ui)
        adapt(self.model, ExtendedAccess).load(element, ui)

        self.set_all_literals(element)
