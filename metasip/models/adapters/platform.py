# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


from .base_adapter import AttributeType, BaseAdapter


class PlatformAdapter(BaseAdapter):
    """ This is the Platform adapter. """

    # The map of attribute names and types.
    ATTRIBUTE_TYPE_MAP = {
        'inputdirpattern':  AttributeType.STRING,
        'name':             AttributeType.STRING,
        'parserargs':       AttributeType.STRING,
    }

    def save(self, output):
        """ Save the model to an output file. """

        output.write(f'<Platform name="{self.model.name}"')
        self.save_str('inputdirpattern', output)
        self.save_str('parserargs', output)
        output.write('/>\n')
