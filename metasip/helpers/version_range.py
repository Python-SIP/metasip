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


def version_range(version_range):
    """ Return a version range as a string. """

    if version_range.startversion == '':
        if version_range.endversion == '':
            # This should never happen.
            return ''

        return '- ' + version_range.endversion

    if version_range.endversion == '':
        return version_range.startversion + ' -'

    return version_range.startversion + ' - ' + version_range.endversion
