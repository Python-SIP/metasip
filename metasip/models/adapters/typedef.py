# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


from ..annos import Annos
from ..code import Code
from ..docstring import Docstring

from .adapt import adapt
from .base_adapter import AttributeType, BaseApiAdapter


class TypedefAdapter(BaseApiAdapter):
    """ This is the Typedef adapter. """

    # The map of attribute names and types.
    ATTRIBUTE_TYPE_MAP = {
        'name': AttributeType.STRING,
        'type': AttributeType.STRING,
    }

    def __eq__(self, other):
        """ Compare for C/C++ equality. """

        typedef = self.model
        other_typedef = other.model

        if type(typedef) is not type(other_typedef):
            return False

        if typedef.name != other_typedef.name:
            return False

        if self.expand_type(typedef.type) != self.expand_type(other_typedef.type):
            return False

        return True

    def as_str(self):
        """ Return the standard string representation. """

        typedef = self.model

        return 'typedef ' + self.expand_type(typedef.type, typedef.name) + adapt(typedef, Annos).as_str()

    def generate_sip(self, sip_file, output):
        """ Generate the .sip file content. """

        typedef = self.model

        nr_ends = self.version_start(output)

        output.write(self.as_str())
        output.write(';\n')

        adapt(typedef, Docstring).generate_sip_directives(output)

        self.version_end(nr_ends, output)

    def load(self, element, project, ui):
        """ Load the model from the XML element.  An optional user interface
        may be available to inform the user of progress.
        """

        super().load(element, project, ui)

        adapt(self.model, Code).load(element, project, ui)
        adapt(self.model, Docstring).load(element, project, ui)

    def save(self, output):
        """ Save the model to an output file. """

        typedef = self.model

        output.write('<Typedef')
        adapt(typedef, Code).save_attributes(output)
        adapt(typedef, Docstring).save_attributes(output)
        self.save_attribute('name', typedef.name, output)
        self.save_attribute('type', typedef.type, output)
        output.write('>\n')

        output += 1
        adapt(typedef, Code).save_subelements(output)
        adapt(typedef, Docstring).save_subelements(output)
        output -= 1

        output.write('</Typedef>\n')
