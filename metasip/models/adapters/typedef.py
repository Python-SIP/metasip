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


from ..annos import Annos
from ..code import Code

from .adapt import adapt
from .base_adapter import AttributeType, BaseApiAdapter


class TypedefAdapter(BaseApiAdapter):
    """ This is the Typedef adapter. """

    # The map of attribute names and types.
    ATTRIBUTE_TYPE_MAP = {
        'name': AttributeType.STRING,
        'type': AttributeType.STRING,
    }

    def as_str(self):
        """ Return the standard string representation. """

        typedef = self.model

        return 'typedef ' + self.expand_type(typedef.type, typedef.name) + adapt(typedef, Annos).as_str()

    def generate_sip(self, output):
        """ Generate the .sip file content. """

        # TODO

    def load(self, element, ui):
        """ Load the model from the XML element.  An optional user interface
        may be available to inform the user of progress.
        """

        super().load(element, ui)

        adapt(self.model, Code).load(element, ui)

    def save(self, output):
        """ Save the model to an output file. """

        typedef = self.model

        output.write('<Typedef')
        adapt(typedef, Code).save(output)
        self.save_attribute('name', typedef.name, output)
        self.save_attribute('type', typedef.type, output)
        output.write('/>\n')
