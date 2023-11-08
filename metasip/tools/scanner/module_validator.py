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


from ...dip.model import implements, Model
from ...dip.ui import IValidator


@implements(IValidator)
class ModuleValidator(Model):
    """ ModuleValidator is an internal class that implements a validator for
    strings representing module names.
    """

    def configure(self, editor):
        """ Configure an editor to use this validator.

        :param editor:
            is the editor.
        """

    def validate(self, controller, editor, value):
        """ Validate an editor's value.

        :param controller:
            is the controller.
        :param editor:
            is the editor.
        :param value:
            is the value.
        :return:
            a string describing why the value is invalid.  An empty string is
            returned if the value is valid.
        """

        # A module name is optional.
        if value == '':
            return ''

        # Get the list of module names.
        modules = [m.name for m in controller.current_project.modules]

        return '' if value in modules else "the name of a Python module is required"
