# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


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

    def __eq__(self, other):
        """ Compare for C/C++ equality. """

        variable = self.model
        other_variable = other.model

        if type(variable) is not type(other_variable):
            return False

        if variable.access != other_variable.access:
            return False

        if variable.name != other_variable.name:
            return False

        if self.expand_type(variable.type) != self.expand_type(other_variable.type):
            return False

        if variable.static != other_variable.static:
            return False

        return True

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

    def load(self, element, project, ui):
        """ Load the model from the XML element.  An optional user interface
        may be available to inform the user of progress.
        """

        super().load(element, project, ui)

        adapt(self.model, Code).load(element, project, ui)
        adapt(self.model, Access).load(element, project, ui)

    def save(self, output):
        """ Save the model to an output file. """

        variable = self.model

        output.write('<Variable')
        adapt(variable, Code).save_attributes(output)
        adapt(variable, Access).save_attributes(output)
        self.save_attribute('name', variable.name, output)
        self.save_attribute('type', variable.type, output)
        self.save_bool('static', output)
        output.write('>\n')

        output += 1
        adapt(variable, Code).save_subelements(output)
        adapt(variable, Access).save_subelements(output)
        self.save_literal('accesscode', output)
        self.save_literal('getcode', output)
        self.save_literal('setcode', output)
        output -= 1

        output.write('</Variable>\n')
