# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


from ..helpers import validate_identifier, validation_error


def init_platform_selector(selector, project):
    """ Initialise a platform selector. """

    selector.clear()
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
