# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


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

    def __eq__(self, other):
        """ Compare for C/C++ equality. """

        enum_value = self.model
        other_enum_value = other.model

        if type(enum_value) is not type(other_enum_value):
            return False

        if enum_value.name != other_enum_value.name:
            return False

        return True

    def as_str(self):
        """ Return the standard string representation. """

        enum_value = self.model

        return enum_value.name + adapt(enum_value, Annos).as_str()

    def generate_sip(self, sip_file, output):
        """ Generate the .sip file content. """

        nr_ends = self.version_start(output)

        output.write(self.as_str())
        output.write(',\n')

        self.version_end(nr_ends, output)

    def load(self, element, project, ui):
        """ Load the model from the XML element.  An optional user interface
        may be available to inform the user of progress.
        """

        super().load(element, project, ui)

        adapt(self.model, Annos).load(element, project, ui)
        adapt(self.model, Tagged).load(element, project, ui)
        adapt(self.model, Workflow).load(element, project, ui)

    def save(self, output):
        """ Save the model to an output file. """

        enum_value = self.model

        output.write('<EnumValue')
        adapt(enum_value, Annos).save_attributes(output)
        adapt(enum_value, Workflow).save_attributes(output)
        adapt(enum_value, Tagged).save_attributes(output)
        self.save_attribute('name', enum_value.name, output)
        output.write('>\n')

        output += 1
        adapt(enum_value, Annos).save_subelements(output)
        adapt(enum_value, Tagged).save_subelements(output)
        adapt(enum_value, Workflow).save_subelements(output)
        output -= 1

        output.write('</EnumValue>\n')
