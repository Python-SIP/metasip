# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


from ..helpers import validate_identifier, validation_error


def init_feature_selector(selector, project):
    """ Initialise a feature selector. """

    selector.clear()
    selector.addItems(sorted(project.features + project.externalfeatures))


def validate_feature_name(feature, project, dialog):
    """ Validate a feature name and return True if it is valid. """

    message = validate_identifier(feature, "feature")
    if message is None:
        if feature in project.features:
            message = "A feature has already been defined with the same name."
        elif feature in project.externalfeatures:
            message = "An external feature has already been defined with the same name."

    if message is not None:
        validation_error(message, dialog)
        return False

    return True
