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
from ..callable import Callable

from .adapt import adapt
from .base_adapter import AttributeType, BaseApiAdapter


class OperatorMethodAdapter(BaseApiAdapter):
    """ This is the OperatorMethod adapter. """

    # The map of attribute names and types.
    ATTRIBUTE_TYPE_MAP = {
        'abstract': AttributeType.BOOL_FALSE,
        'const':    AttributeType.BOOL_FALSE,
        'virtual':  AttributeType.BOOL_FALSE,
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

        s += callable_adapter.return_type_as_str(allow_py=True) + method.name

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
        adapt(self.model, Access).load(element, ui)

        self.set_all_literals(element)
