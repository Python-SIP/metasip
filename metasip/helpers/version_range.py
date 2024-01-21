# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


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
