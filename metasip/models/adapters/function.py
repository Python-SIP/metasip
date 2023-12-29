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


from ..callable import Callable
from ..docstring import Docstring

from .adapt import adapt
from .base_adapter import BaseApiAdapter


class FunctionAdapter(BaseApiAdapter):
    """ This is the Function adapter. """

    def as_str(self):
        """ Return the standard string representation. """

        return adapt(self.model, Callable).as_str()

    def generate_sip(self, output):
        """ Generate the .sip file content. """

        function = self.model

        nr_ends = self.version_start(output)

        adapt(function, Callable).generate_sip_detail(output)
        adapt(function, Docstring).generate_sip_detail(output)
        output.write(';\n')
        adapt(function, Docstring).generate_sip_directives(output)
        adapt(function, Callable).generate_sip_directives(output)

        self.version_end(nr_ends, output)

    def load(self, element, ui):
        """ Load the model from the XML element.  An optional user interface
        may be available to inform the user of progress.
        """

        adapt(self.model, Callable).load(element, ui)
        adapt(self.model, Docstring).load(element, ui)

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
