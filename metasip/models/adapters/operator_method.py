# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


from ..access import Access
from ..annos import Annos
from ..callable import Callable

from .adapt import adapt
from .base_adapter import AttributeType, BaseApiAdapter


class OperatorMethodAdapter(BaseApiAdapter):
    """ This is the OperatorMethod adapter. """

    # The map of attribute names and types.
    ATTRIBUTE_TYPE_MAP = {
        'abstract': AttributeType.BOOL,
        'const':    AttributeType.BOOL,
        'virtcode': AttributeType.LITERAL,
        'virtual':  AttributeType.BOOL,
    }

    def __eq__(self, other):
        """ Compare for C/C++ equality. """

        method = self.model
        other_method = other.model

        if type(method) is not type(other_method):
            return False

        if adapt(method, Callable) != adapt(other_method, Callable):
            return False

        if method.access != other_method.access:
            return False

        if method.virtual != other_method.virtual:
            return False

        if method.const != other_method.const:
            return False

        if method.abstract != other_method.abstract:
            return False

        return True

    def as_str(self):
        """ Return the standard string representation. """

        # We can't use the super class version because we might need to stick
        # some text in the middle of it.

        method = self.model

        callable_adapter = adapt(method, Callable)

        s = ''

        if method.virtual:
            s += 'virtual '

        s += callable_adapter.return_type_as_str(allow_py=True) + 'operator' + method.name

        if method.pyargs != '':
            s += method.pyargs
        else:
            args = ', '.join([adapt(arg).as_py_str() for arg in method.args])
            s += '(' + args + ')'

        if method.const:
            s += ' const'

        if method.abstract:
            s += ' = 0'

        s += adapt(method, Annos).as_str()

        if (method.virtual or method.access.startswith('protected') or method.methcode == '') and callable_adapter.has_different_signatures():
            return_type = callable_adapter.return_type_as_str().strip()
            args = ', '.join([adapt(arg).as_str() for arg in method.args])
            s += f' [{return_type} ({args})]'

        return s

    def generate_sip(self, sip_file, output):
        """ Generate the .sip file content. """

        method = self.model

        nr_ends = self.version_start(output)

        output.write(self.as_str())
        output.write(';\n')

        adapt(method, Callable).generate_sip_directives(output)
        adapt(method, Access).generate_sip_directives(output)
        output.write_code_directive('%VirtualCatcherCode', method.virtcode)

        self.version_end(nr_ends, output)

    def load(self, element, project, ui):
        """ Load the model from the XML element.  An optional user interface
        may be available to inform the user of progress.
        """

        super().load(element, project, ui)

        adapt(self.model, Callable).load(element, project, ui)
        adapt(self.model, Access).load(element, project, ui)

    def save(self, output):
        """ Save the model to an output file. """

        method = self.model

        output.write('<OperatorMethod')
        adapt(method, Callable).save_attributes(output)
        adapt(method, Access).save_attributes(output)
        self.save_bool('virtual', output)
        self.save_bool('const', output)
        self.save_bool('abstract', output)
        output.write('>\n')

        output += 1
        adapt(method, Callable).save_subelements(output)
        adapt(method, Access).save_subelements(output)
        self.save_literal('virtcode', output)
        output -= 1

        output.write('</OperatorMethod>\n')
