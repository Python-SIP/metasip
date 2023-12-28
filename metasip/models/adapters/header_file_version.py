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


class HeaderFileVersionAdapter(BaseAdapter):
    """ This is the HeaderFileVersion adapter. """

    # The map of attribute names and types.
    ATTRIBUTE_TYPE_MAP = {
        'md5':      AttributeType.STRING,
        'parse':    AttributeType.BOOL,
        'version':  AttributeType.STRING,
    }

    def save(self, output):
        """ Save the model to an output file. """

        header_file_version = self.model

        output.write(f'<HeaderFileVersion md5="{header_file_version.md5}" version="{header_file_version.version}"')
        self.save_bool('parse', output)
        output.write('/>\n')
