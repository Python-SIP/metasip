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
from ..callable import Callable

from .adapt import adapt
from .base_adapter import AttributeType, BaseApiAdapter


class OperatorCastAdapter(BaseApiAdapter):
    """ This is the OperatorCast adapter. """

    # The map of attribute names and types.
    ATTRIBUTE_TYPE_MAP = {
        'const':    AttributeType.BOOL,
    }

    def as_str(self):
        """ Return the standard string representation. """

        cast = self.model

        s = 'operator ' + adapt(cast, Callable).as_str()

        if cast.const:
            s += ' const'

        return s

    def generate_sip(self, sip_file, output):
        """ Generate the .sip file content. """

        cast = self.model

        nr_ends = self.version_start(output)

        output.write(self.as_str())
        output.write(';\n')

        adapt(cast, Callable).generate_sip_directives(output)
        adapt(cast, Access).generate_sip_directives(output)

        self.version_end(nr_ends, output)

    def load(self, element, ui):
        """ Load the model from the XML element.  An optional user interface
        may be available to inform the user of progress.
        """

        super().load(element, ui)

        adapt(self.model, Callable).load(element, ui)
        adapt(self.model, Access).load(element, ui)

    def save(self, output):
        """ Save the model to an output file. """

        cast = self.model

        output.write('<OperatorCast')
        adapt(cast, Callable).save_attributes(output)
        adapt(cast, Access).save_attributes(output)
        self.save_bool('const', output)
        output.write('>\n')

        output += 1
        adapt(cast, Callable).save_subelements(output)
        adapt(cast, Access).save_subelements(output)
        output -= 1

        output.write('</OperatorCast>\n')
