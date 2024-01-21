# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


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
        for module in project.modules:
            if module.name == module_name:
                project.modules.remove(module)
                break
        else:
            project.externalmodules.remove(module)

        self.shell.notify(EventType.MODULE_DELETE, module)

        return True
