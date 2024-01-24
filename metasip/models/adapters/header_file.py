# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


from ..header_file_version import HeaderFileVersion

from .adapt import adapt
from .base_adapter import AttributeType, BaseAdapter


class HeaderFileAdapter(BaseAdapter):
    """ This is the HeaderFile adapter. """

    # The map of attribute names and types.
    ATTRIBUTE_TYPE_MAP = {
        'ignored':  AttributeType.BOOL,
        'module':   AttributeType.STRING,
        'name':     AttributeType.STRING,
    }

    def load(self, element, project, ui):
        """ Load the model from the XML element.  An optional user interface
        may be available to inform the user of progress.
        """

        super().load(element, project, ui)

        for subelement in element:
            if subelement.tag == 'HeaderFileVersion':
                header_file_version = HeaderFileVersion()
                adapt(header_file_version).load(subelement, project, ui)
                self.model.versions.append(header_file_version)

    def save(self, output):
        """ Save the model to an output file. """

        header_file = self.model

        output.write(f'<HeaderFile name="{header_file.name}"')
        self.save_str('module', output)
        self.save_bool('ignored', output)
        output.write('>\n')
        output += 1

        for header_file_version in header_file.versions:
            adapt(header_file_version).save(output)

        output -= 1
        output.write('</HeaderFile>\n')
