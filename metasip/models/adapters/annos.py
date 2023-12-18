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


class AnnosAdapter(BaseAdapter):
    """ This is the Annos adapter. """

    # The map of attribute names and types.
    ATTRIBUTE_TYPE_MAP = {
        'annos':    AttributeType.STRING,
    }

    def as_sip(self, project):
        """ Return the standard .sip file representation. """

        annos = self.model.annos

        return f' /{annos}/' if annos != '' else ''
