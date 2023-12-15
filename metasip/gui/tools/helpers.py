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


import re

from ...models import CodeContainerMixin, EnumModel

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
        if isinstance(code, EnumModel):
            for enum_value in code.content:
                yield (enum_value, code)
        elif isinstance(code, CodeContainerMixin):
            for item in _tagged_from_container(code):
                yield item

        yield (code, container)
