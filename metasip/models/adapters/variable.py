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


class VariableAdapter(BaseApiAdapter):
    """ This is the Variable adapter. """

    # The map of attribute names and types.
    ATTRIBUTE_TYPE_MAP = {
        'accesscode':   AttributeType.LITERAL,
        'getcode':      AttributeType.LITERAL,
        'name':         AttributeType.STRING,
        'setcode':      AttributeType.LITERAL,
        'static':       AttributeType.BOOL,
        'type':         AttributeType.STRING,
    }

    def as_str(self):
        """ Return the standard string representation. """

        variable = self.model

        s = self.expand_type(variable.type, variable.name) + adapt(variable, Annos).as_str()

        if variable.static:
            s = 'static ' + s

        return s

    def generate_sip(self, sip_file, output):
        """ Generate the .sip file content. """

        variable = self.model

        nr_ends = self.version_start(output)

        output.write(self.as_str())

        need_brace = variable.accesscode != '' or variable.getcode != '' or variable.setcode != ''

        if need_brace:
            output.write(' {\n', indent=False)

        output.write_code_directive('%AccessCode', variable.accesscode)
        output.write_code_directive('%GetCode', variable.getcode)
        output.write_code_directive('%SetCode', variable.setcode)

        if need_brace:
            output.write('}')

        output.write(';\n', indent=False)

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

        variable = self.model

        output.write('<Variable')
        adapt(variable, Code).save_attributes(output)
        adapt(variable, Access).save_attributes(output)
        self.save_attribute('name', variable.name, output)
        self.save_attribute('type', variable.type, output)
        self.save_bool('static', output)

        # Note that this assumes all model super-classes do not have
        # subelements.
        if variable.accesscode != '' or variable.getcode != '' or variable.setcode != '':
            output.write('>\n')

            output += 1
            self.save_literal('accesscode', output)
            self.save_literal('getcode', output)
            self.save_literal('setcode', output)
            output -= 1

            output.write('</Variable>\n')
        else:
            output.write('/>\n')
