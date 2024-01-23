# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


from .base_adapter import AttributeType, BaseAdapter


class AnnosAdapter(BaseAdapter):
    """ This is the Annos adapter. """

    # The map of attribute names and types.
    ATTRIBUTE_TYPE_MAP = {
        'annos':    AttributeType.STRING,
    }

    def as_str(self):
        """ Return the standard string representation. """

        annos = self.model.annos

        return f' /{annos}/' if annos != '' else ''

    def save_attributes(self, output):
        """ Save the XML attributes. """

        self.save_str('annos', output)
