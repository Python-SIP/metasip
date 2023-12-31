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
        'unnamed':      AttributeType.BOOL,
    }

    def __eq__(self, other):
        """ Compare for C/C++ equality. """

        arg = self.model
        other_arg = other.model

        if type(arg) is not type(other_arg):
            return False

        if self.expand_type(arg.type) != self.expand_type(other_arg.type):
            return False

        if arg.default != other_arg.default:
            return False

        return True

    def as_py_str(self):
        """ Return the Python representation of the argument. """

        arg = self.model

        s = self.expand_type(arg.pytype if arg.pytype != '' else arg.type,
                name=arg.name)

        s += adapt(arg, Annos).as_str()

        if arg.pydefault != '':
            s += ' = ' + arg.pydefault
        elif arg.default != '':
            s += ' = ' + arg.default

        return s

    def as_str(self):
        """ Return the standard string representation. """

        arg = self.model

        s = self.expand_type(arg.type, name=arg.name)

        if arg.default != '':
            s += ' = ' + arg.default

        return s

    def generate_sip(self, sip_file, output):
        """ Generate the .sip file content. """

        output.write(self.as_py_str())

    def load(self, element, ui):
        """ Load the model from the XML element.  An optional user interface
        may be available to inform the user of progress.
        """

        super().load(element, ui)

        adapt(self.model, Annos).load(element, ui)

    def save(self, output):
        """ Save the model to an output file. """

        argument = self.model

        output.write('<Argument')
        adapt(argument, Annos).save_attributes(output)
        self.save_attribute('type', argument.type, output)
        self.save_bool('unnamed', output)
        self.save_str('name', output)
        self.save_str('default', output)
        self.save_str('pydefault', output)
        self.save_str('pytype', output)

        # Note that we are assuming Annos does not have any subelements.
        output.write('/>\n')
