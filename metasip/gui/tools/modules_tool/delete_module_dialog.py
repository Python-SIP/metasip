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


from PyQt6.QtWidgets import QComboBox

from ...helpers import BaseDialog
from ...shell import EventType

from .helpers import init_module_selector


class DeleteModuleDialog(BaseDialog):
    """ This class implements the dialog for deleting a module. """

    def populate(self, layout):
        """ Populate the dialog's layout. """

        self._module = QComboBox()
        layout.addWidget(self._module)

    def set_fields(self):
        """ Set the dialog's fields from the project. """

        init_module_selector(self._module, self.model)

    def get_fields(self):
        """ Update the project from the dialog's fields. """

        project = self.model

        module_name = self._module.currentText()

        # Delete from the project's list.
        # TODO - lots of additional events should be generated below.
        for module in project.modules:
            if module.name == module_name:
                project.modules.remove(module)
                break
        else:
            project.externalmodules.remove(module)

        self.shell.notify(EventType.MODULE_ADD_DELETE)

        return True
