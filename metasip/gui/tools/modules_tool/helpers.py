# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


from ..helpers import validate_identifier, validation_error


def init_module_selector(selector, project):
    """ Initialise a module selector. """

    module_names = [module.name for module in project.modules]
    module_names.extend(project.externalmodules)

    selector.clear()
    selector.addItems(sorted(module_names))


def validate_module_name(module_name, project, dialog):
    """ Validate a module name and return True if it is valid. """

    message = validate_identifier(module_name, "module")
    if message is None:
        for module in project.modules:
            if module.name == module_name:
                message = "A module has already been defined with the same name."
                break
        else:
            if module_name in project.externalmodules:
                message = "An external module has already been defined with the same name."

    if message is not None:
        validation_error(message, dialog)
        return False

    return True
