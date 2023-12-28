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

from .adapt import adapt
from .base_adapter import BaseApiAdapter


class OperatorFunctionAdapter(BaseApiAdapter):
    """ This is the OperatorFunction adapter. """

    def as_str(self):
        """ Return the standard string representation. """

        function = self.model

        callable_adapter = adapt(function, Callable)

        s = callable_adapter.return_type_as_str(allow_py=True) + 'operator' + function.name

        if function.pyargs != '':
            s += function.pyargs
        else:
            args = ', '.join([adapt(arg).as_py_str() for arg in function.args])
            s += '(' + args + ')'

        s += adapt(function, Annos).as_str()

        if callable_adapter.has_different_signatures():
            return_type = callable_adapter.return_type_as_str()
            args = ', '.join([adapt(arg).as_str() for arg in function.args])
            s += f' [{return_type} ({args})]'

        return s

    def generate_sip(self, output):
        """ Generate the .sip file content. """

        # TODO

    def load(self, element, ui):
        """ Load the model from the XML element.  An optional user interface
        may be available to inform the user of progress.
        """

        adapt(self.model, Callable).load(element, ui)

    def save(self, output):
        """ Save the model to an output file. """

        function = self.model

        output.write('<OperatorFunction')
        adapt(function, Callable).save_attributes(output)
        output.write('>\n')

        output += 1
        adapt(function, Callable).save_subelements(output)
        output -= 1

        output.write('</OperatorFunction>\n')
