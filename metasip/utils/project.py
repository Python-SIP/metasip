# Copyright (c) 2013 Riverbank Computing Limited.
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

from ..interfaces.project import ICodeContainer, IEnum


def ITagged_items(project):
    """ A generator of 2-tuples of all API items that implement ITagged and
    the API item that contains it.  The values are in depth first order.
    """

    for module in project.modules:
        for sip_file in module.content:
            for item in _tagged_from_container(sip_file):
                yield item


def _tagged_from_container(container):
    """ A sub-generator for the items in a container. """

    for code in container.content:
        # Depth first.
        if isinstance(code, IEnum):
            for enum_value in code.content:
                yield (enum_value, code)
        elif isinstance(code, ICodeContainer):
            for item in _tagged_from_container(code):
                yield item

        yield (code, container)


# The regular expression used to validate an identifier.
_identifier_re = re.compile(r'[_A-Z][_A-Z0-9]*', re.ASCII|re.IGNORECASE)

def validate_identifier(identifier, identifier_type):
    """ Validate an identifier and return an error message describing why it is
    invalid, or an empty string if it is valid.
    """

    if identifier == '':
        return "A {0} name is required.".format(identifier_type)

    if not _identifier_re.match(identifier):
        return "A {0} name can only contain underscores, ASCII letters and digits and cannot start with a digit.".format(identifier_type)

    return ""
