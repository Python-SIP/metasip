# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


from ..models import VersionRange


class VersionMap:
    """ This class is a tool for consolidating and normalising ranges of
    versions.
    """

    def __init__(self, project, version_ranges=None):
        """ Return a version map with each entry set to an initial value. """

        self._versions = project.versions
        self._initialise_map(False)

        if version_ranges is not None:
            self.update_from_version_ranges(version_ranges)

    def __bool__(self):
        """ Return True if the version map is unconditionally True. """

        return all(self._map)

    def __getitem__(self, version):
        """ Return the map value for a version. """

        return self._map[self._versions.index(version)]

    def __setitem__(self, version, value):
        """ Set the map value for a version. """

        self._map[self._versions.index(version)] = value

    def update_from_version_ranges(self, version_ranges):
        """ Update the version map from a list of version ranges. """

        # No version ranges means all versions are valid.
        if len(version_ranges) == 0:
            self._initialise_map(True)
            return

        for version_range in version_ranges:
            if version_range.startversion == '':
                start_idx = 0
            else:
                start_idx = self._versions.index(version_range.startversion)

            if version_range.endversion == '':
                end_idx = len(self._versions)
            else:
                end_idx = self._versions.index(version_range.endversion)

            for i in range(start_idx, end_idx):
                self._map[i] = True

    def as_version_ranges(self):
        """ Convert a version map to a list of version ranges.  An empty list
        means it is unconditionally True, None means it is unconditionally
        False.
        """

        # See if the item is valid for all versions.
        if all(self._map):
            return []

        # See if the item is valid for no versions.
        for v in self._map:
            if v:
                break
        else:
            return None

        # Construct the new list of version ranges.
        version_ranges = []
        vrange = None

        for idx, v in enumerate(self._map):
            if v:
                # Start a new version range if there isn't one currently.
                if vrange is None:
                    vrange = VersionRange()

                    if idx != 0:
                        vrange.startversion = self._versions[idx]
            elif vrange is not None:
                vrange.endversion = self._versions[idx]
                version_ranges.append(vrange)
                vrange = None

        if vrange is not None:
            version_ranges.append(vrange)

        return version_ranges

    def _initialise_map(self, initial_state):
        """ Initialise the map. """

        self._map = [initial_state for v in self._versions]
