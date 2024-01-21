# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


import re

from ...models import CodeContainer, Enum

from ..helpers import warning


# The regular expression used to validate an identifier.
_identifier_re = re.compile(r'[_A-Z][_A-Z0-9]*', re.ASCII|re.IGNORECASE)

def validate_identifier(identifier, identifier_type):
    """ Validate an identifier and return an error message describing why it is
    invalid, or None if it is valid.
    """

    if identifier == '':
        return f"A {identifier_type} name is required."

    if not _identifier_re.match(identifier):
        return f"A {identifier_type} name can only contain underscores, ASCII letters and digits and cannot start with a digit."

    return None


def validation_error(message, dialog):
    """ Display a validation error message from a dialog. """

    warning(dialog.widget.windowTitle(), message, parent=dialog.widget)


def tagged_items(project):
    """ A generator of 2-tuples of all API items that can have a tag (feature,
    platform or version) and the API item that contains it.  The values are in
    depth first order.
    """

    for module in project.modules:
        for sip_file in module.content:
            for item in _tagged_from_container(sip_file):
                yield item


def _tagged_from_container(container):
    """ A sub-generator for the items in a container. """

    for code in container.content:
        # Depth first.
        if isinstance(code, Enum):
            for enum_value in code.content:
                yield (enum_value, code)
        elif isinstance(code, CodeContainer):
            for item in _tagged_from_container(code):
                yield item

        yield (code, container)
