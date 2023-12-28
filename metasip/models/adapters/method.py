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
from ..callable import Callable
from ..docstring import Docstring
from ..extended_access import ExtendedAccess

from .adapt import adapt
from .base_adapter import AttributeType, BaseApiAdapter


class MethodAdapter(BaseApiAdapter):
    """ This is the Method adapter. """

    ATTRIBUTE_TYPE_MAP = {
        'abstract': AttributeType.BOOL,
        'const':    AttributeType.BOOL,
        'final':    AttributeType.BOOL,
        'static':   AttributeType.BOOL,
        'virtcode': AttributeType.LITERAL,
        'virtual':  AttributeType.BOOL,
    }

    def as_str(self):
        """ Return the standard string representation. """

        # We can't use the super class version because we might need to stick
        # some text in the middle of it.

        method = self.model

        callable_adapter = adapt(method, Callable)

        s = ''

        if method.virtual:
            s += 'virtual '

        if method.static:
            s += 'static '

        s += callable_adapter.return_type_as_str(allow_py=True) + method.name

        if method.pyargs != '':
            s += method.pyargs
        else:
            args = ', '.join([adapt(arg).as_py_str() for arg in method.args])
            s += '(' + args + ')'

        if method.const:
            s += ' const'

        if method.final:
            s += ' final'

        if method.abstract:
            s += ' = 0'

        s += adapt(method, Annos).as_str()

        if callable_adapter.has_different_signatures():
            return_type = callable_adapter.return_type_as_str()
            args = ', '.join([adapt(arg).as_str() for arg in method.args])
            s += f' [{return_type} ({args})]'

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
        adapt(self.model, Docstring).load(element, ui)
        adapt(self.model, ExtendedAccess).load(element, ui)

    def save(self, output):
        """ Save the model to an output file. """

        method = self.model

        output.write('<Method')
        adapt(method, Callable).save_attributes(output)
        adapt(method, Docstring).save_attributes(output)
        adapt(method, ExtendedAccess).save_attributes(output)
        self.save_bool('virtual', output)
        self.save_bool('const', output)
        self.save_bool('final', output)
        self.save_bool('static', output)
        self.save_bool('abstract', output)
        output.write('>\n')

        output += 1
        adapt(method, Callable).save_subelements(output)
        adapt(method, Docstring).save_subelements(output)
        adapt(method, ExtendedAccess).save_subelements(output)
        self.save_literal('virtcode', output)
        output -= 1

        output.write('</Method>\n')
