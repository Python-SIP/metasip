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


from ..annos import Annos

from .adapt import adapt
from .base_adapter import AttributeType, BaseApiAdapter


class ArgumentAdapter(BaseApiAdapter):
    """ This is the Argument adapter. """

    # The map of attribute names and types.
    ATTRIBUTE_TYPE_MAP = {
        'default':      AttributeType.STRING,
        'name':         AttributeType.STRING,
        'pydefault':    AttributeType.STRING,
        'pytype':       AttributeType.STRING,
        'type':         AttributeType.STRING,
        'unnamed':      AttributeType.BOOL_TRUE,
    }

    def as_str(self):
        """ Return the standard string representation. """

        arg = self.model

        s = self.expand_type(arg.type, name=arg.name)

        s += adapt(arg, Annos).as_sip()

        if arg.pydefault != '':
            s += ' = ' + arg.pydefault
        elif arg.default != '':
            s += ' = ' + arg.default

        return s

    def generate_sip(self, output):
        """ Generate the .sip file content. """

        # TODO

    def load(self, element, ui):
        """ Load the model from the XML element.  An optional user interface
        may be available to inform the user of progress.
        """

        super().load(element, ui)

        adapt(self.model, Annos).load(element, ui)
