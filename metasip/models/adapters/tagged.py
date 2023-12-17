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


from ..version_range import VersionRange

from .base_adapter import AttributeType, BaseAdapter


class TaggedAdapter(BaseAdapter):
    """ This is the Tagged adapter. """

    # The map of attribute names and types.
    ATTRIBUTE_TYPE_MAP = {
        'features':     AttributeType.STRING_LIST,
        'platforms':    AttributeType.STRING_LIST,
    }

    def load(self, element, ui):
        """ Load the model from the XML element.  An optional user interface
        may be available to inform the user of progress.
        """

        # Load the simple attributes.
        super().load(element, ui)

        versions = elem.get('versions')

        if versions is not None:
            for version in versions.split():
                version_range = VersionRange()
                version_range.startversion, version_range.endversion = version.split('-')
                self.model.versions.append(version_range)