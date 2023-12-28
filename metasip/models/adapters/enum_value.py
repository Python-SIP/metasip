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
from ..tagged import Tagged
from ..workflow import Workflow

from .adapt import adapt
from .base_adapter import AttributeType, BaseApiAdapter


class EnumValueAdapter(BaseApiAdapter):
    """ This is the EnumValue adapter. """

    # The map of attribute names and types.
    ATTRIBUTE_TYPE_MAP = {
        'name': AttributeType.STRING,
    }

    def as_str(self):
        """ Return the standard string representation. """

        return self.model.name

    def generate_sip(self, output):
        """ Generate the .sip file content. """

        # TODO

    def load(self, element, ui):
        """ Load the model from the XML element.  An optional user interface
        may be available to inform the user of progress.
        """

        super().load(element, ui)

        adapt(self.model, Annos).load(element, ui)
        adapt(self.model, Tagged).load(element, ui)
        adapt(self.model, Workflow).load(element, ui)

    def save(self, output):
        """ Save the model to an output file. """

        enum_value = self.model

        output.write('<Typedef')
        adapt(enum_value, Annos).save_attributes(output)
        adapt(enum_value, Tagged).save_attributes(output)
        adapt(enum_value, Workflow).save_attributes(output)
        self.save_attribute('name', enum_value.name, output)

        # Note that we are assuming model super-classes do not have any
        # subelements.
        output.write('/>\n')
