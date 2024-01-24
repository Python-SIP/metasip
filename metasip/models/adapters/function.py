# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


from ..annos import Annos
from ..callable import Callable
from ..docstring import Docstring

from .adapt import adapt
from .base_adapter import BaseApiAdapter


class FunctionAdapter(BaseApiAdapter):
    """ This is the Function adapter. """

    def __eq__(self, other):
        """ Compare for C/C++ equality. """

        function = self.model
        other_function = other.model

        if type(function) is not type(other_function):
            return False

        if adapt(function, Callable) != adapt(other_function, Callable):
            return False

        return True

    def as_str(self):
        """ Return the standard string representation. """

        return adapt(self.model, Callable).as_str()

    def generate_sip(self, sip_file, output):
        """ Generate the .sip file content. """

        function = self.model

        nr_ends = self.version_start(output)

        # Note that we don't use CallableAdapter's implementation because we
        # dont want any C/C++ signature.

        s = adapt(function, Callable).return_type_as_str(allow_py=True) + function.name

        if function.pyargs != '':
            s += function.pyargs
        else:
            args = ', '.join([adapt(arg).as_py_str() for arg in function.args])
            s += '(' + args + ')'

        s += adapt(function, Annos).as_str()
        output.write(s)
        output.write(';\n')

        adapt(function, Docstring).generate_sip_directives(output)
        adapt(function, Callable).generate_sip_directives(output)

        self.version_end(nr_ends, output)

    def load(self, element, project, ui):
        """ Load the model from the XML element.  An optional user interface
        may be available to inform the user of progress.
        """

        adapt(self.model, Callable).load(element, project, ui)
        adapt(self.model, Docstring).load(element, project, ui)

    def save(self, output):
        """ Save the model to an output file. """

        function = self.model

        output.write('<Function')
        adapt(function, Callable).save_attributes(output)
        adapt(function, Docstring).save_attributes(output)
        output.write('>\n')

        output += 1
        # The order is to match older versions.
        adapt(function, Docstring).save_subelements(output)
        adapt(function, Callable).save_subelements(output)
        output -= 1

        output.write('</Function>\n')
