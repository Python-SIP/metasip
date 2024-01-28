# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


import sys


def get_platform_name():
    """ Return the name of the current platform. """

    if sys.platform == 'darwin':
        return 'macOS'

    if sys.platform == 'win32':
        return 'Windows'

    platform_name = 'Linux'


def get_supported_platforms():
    """ Return the names of supported host platforms. """

    return ('Linux', 'macOS', 'Windows')


def header_directory_platform(header_directory, platform_name=None):
    """ Return a header directory's  Platform instance for a platform. """

    if platform_name is None:
        platform_name = get_platform_name()

    for platform in header_directory.platforms:
        if platform.name == platform_name:
            return platform
