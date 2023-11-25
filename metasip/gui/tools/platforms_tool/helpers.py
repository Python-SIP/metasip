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


from ..helpers import validate_identifier, validation_error


def init_platform_selector(selector, project):
    """ Initialise a platform selector. """

    while selector.count() != 0:
        selector.removeItem(0)

    selector.addItems(sorted(project.platforms))


def validate_platform_name(platform, project, dialog):
    """ Validate a platform name and return True if it is valid. """

    message = validate_identifier(platform, "platform")
    if message is None:
        if platform in project.platforms:
            message = "A platform has already been defined with the same name."

    if message is not None:
        validation_error(message, dialog)
        return False

    return True
