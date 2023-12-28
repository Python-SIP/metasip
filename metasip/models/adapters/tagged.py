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

        versions = element.get('versions')

        if versions is not None:
            for version in versions.split():
                version_range = VersionRange()
                version_range.startversion, version_range.endversion = version.split('-')
                self.model.versions.append(version_range)

    def save_attributes(self, output):
        """ Save the XML attributes. """

        versions = self.versions_as_str(as_xml=True)
        if versions != '':
            self.save_attribute('versions', versions, output)

        self.save_str_list('platforms', output)
        self.save_str_list('features', output)

    def versions_as_str(self, as_xml=False):
        """ Return the standard string representation of the versions. """

        if as_xml:
            separator = ' '
            left_dash = middle_dash = right_dash = '-'
        else:
            separator = ', '
            left_dash = '- '
            middle_dash = ' - '
            right_dash = ' -'

        version_ranges = []

        for version_range in self.model.versions:
            startversion = version_range.startversion
            endversion = version_range.endversion

            if startversion == '':
                if endversion == '':
                    # This should never happen.
                    continue

                version_ranges.append(left_dash + endversion)
            elif endversion == '':
                version_ranges.append(startversion + right_dash)
            else:
                version_ranges.append(startversion + middle_dash + endversion)

        return separator.join(version_ranges)
