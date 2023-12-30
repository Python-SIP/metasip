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


from .base_adapter import AttributeType, BaseAdapter


class DocstringAdapter(BaseAdapter):
    """ This is the Docstring adapter. """

    # The map of attribute names and types.
    ATTRIBUTE_TYPE_MAP = {
        'docstring':    AttributeType.LITERAL,
    }

    def generate_sip_directives(self, output):
        """ Write any directives to a .sip file. """

        output.write_code_directive('%Docstring', self.model.docstring,
                indent=False)

    def save_subelements(self, output):
        """ Save the XML subelements. """

        self.save_literal('docstring', output)
