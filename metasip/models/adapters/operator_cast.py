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


from ..access import Access
from ..callable import Callable

from .adapt import adapt
from .base_adapter import AttributeType, BaseApiAdapter


class OperatorCastAdapter(BaseApiAdapter):
    """ This is the OperatorCast adapter. """

    # The map of attribute names and types.
    ATTRIBUTE_TYPE_MAP = {
        'const':    AttributeType.BOOL_FALSE,
    }

    def as_str(self):
        """ Return the standard string representation. """

        cast = self.model

        s = adapt(cast, Callable).as_str()

        if cast.const:
            s += ' const'

        return s

    def generate_sip(self, output):
        """ Generate the .sip file content. """

        # TODO

    def load(self, element, ui):
        """ Load the model from the XML element.  An optional user interface
        may be available to inform the user of progress.
        """

        super().load(element, ui)

        adapt(self.model, Callable).load(element, ui)
        adapt(self.model, Access).load(element, ui)
