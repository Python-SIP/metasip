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

    def load(self, element, ui):
        """ Load the model from the XML element.  An optional user interface
        may be available to inform the user of progress.
        """

        super().load(element, ui)

        for subelement in element:
            if subelement.tag == 'HeaderFileVersion':
                header_file_version = HeaderFileVersion()
                adapt(header_file_version).load(subelement, ui)
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
