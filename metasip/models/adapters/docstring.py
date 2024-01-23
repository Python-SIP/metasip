# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


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
