# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


from ...helpers import version_range

from ..version_range import VersionRange

from .base_adapter import AttributeType, BaseAdapter


class TaggedAdapter(BaseAdapter):
    """ This is the Tagged adapter. """

    # The map of attribute names and types.
    ATTRIBUTE_TYPE_MAP = {
        'features':     AttributeType.STRING_LIST,
        'platforms':    AttributeType.STRING_LIST,
    }

    def load(self, element, project, ui):
        """ Load the model from the XML element.  An optional user interface
        may be available to inform the user of progress.
        """

        # Load the simple attributes.
        super().load(element, project, ui)

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

        version_ranges = []

        for version in self.model.versions:
            version_range_s = version_range(version)

            if as_xml:
                version_range_s = version_range_s.replace(' ', '')

            version_ranges.append(version_range_s)

        separator = ' ' if as_xml else ', '

        return separator.join(version_ranges)
