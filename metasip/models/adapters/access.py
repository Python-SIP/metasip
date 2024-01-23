# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


from .base_adapter import AttributeType, BaseAdapter


class AccessAdapter(BaseAdapter):
    """ This is the Access adapter. """

    # The map of attribute names and types.
    ATTRIBUTE_TYPE_MAP = {
        'access':   AttributeType.STRING,
    }

    def save_attributes(self, output):
        """ Save the XML attributes. """

        self.save_str('access', output)
