# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


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
