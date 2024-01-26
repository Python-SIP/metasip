# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


from ..access import Access
from ..annos import Annos
from ..code import Code

from .adapt import adapt
from .base_adapter import AttributeType, BaseApiAdapter


class OpaqueClassAdapter(BaseApiAdapter):
    """ This is the OpaqueClass adapter. """

    # The map of attribute names and types.
    ATTRIBUTE_TYPE_MAP = {
        'name': AttributeType.STRING,
    }

    def __eq__(self, other):
        """ Compare for C/C++ equality. """

        klass = self.model
        other_klass = other.model

        if type(klass) is not type(other_klass):
            return False

        if klass.access != other_klass.access:
            return False

        if klass.name != other_klass.name:
            return False

        return True

    def as_str(self):
        """ Return the standard string representation. """

        opaque_class = self.model

        return 'class ' + opaque_class.name + adapt(opaque_class, Annos).as_str()

    def generate_sip(self, sip_file, output):
        """ Generate the .sip file content. """

        nr_ends = self.version_start(output)

        output.write(self.as_str())
        output.write(';\n')

        self.version_end(nr_ends, output)

    def load(self, element, project, ui):
        """ Load the model from the XML element.  An optional user interface
        may be available to inform the user of progress.
        """

        super().load(element, project, ui)

        adapt(self.model, Code).load(element, project, ui)
        adapt(self.model, Access).load(element, project, ui)

    def save(self, output):
        """ Save the model to an output file. """

        opaque_class = self.model

        output.write('<OpaqueClass')
        adapt(opaque_class, Code).save_attributes(output)
        adapt(opaque_class, Access).save_attributes(output)
        self.save_attribute('name', opaque_class.name, output)
        output.write('>\n')

        output += 1
        adapt(opaque_class, Code).save_subelements(output)
        adapt(opaque_class, Access).save_subelements(output)
        output -= 1

        output.write('</OpaqueClass>\n')
