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

    def load(self, element, ui):
        """ Load the model from the XML element.  An optional user interface
        may be available to inform the user of progress.
        """

        super().load(element, ui)

        adapt(self.model, Code).load(element, ui)
        adapt(self.model, Access).load(element, ui)

    def save(self, output):
        """ Save the model to an output file. """

        opaque_class = self.model

        output.write('<OpaqueClass')
        adapt(opaque_class, Code).save_attributes(output)
        adapt(opaque_class, Access).save_attributes(output)
        self.save_attribute('name', opaque_class.name, output)

        # Note that we are assuming model super-classes do not have any
        # subelements.
        output.write('/>\n')
