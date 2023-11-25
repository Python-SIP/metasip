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
