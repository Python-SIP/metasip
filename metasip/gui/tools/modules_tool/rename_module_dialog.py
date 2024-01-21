# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


from PyQt6.QtWidgets import QComboBox, QFormLayout, QLineEdit

from ...helpers import BaseDialog
from ...shell import EventType

from ..helpers import tagged_items

from .helpers import init_module_selector, validate_module_name


class RenameModuleDialog(BaseDialog):
    """ This class implements the dialog for renaming a module. """

    def populate(self, layout):
        """ Populate the dialog's layout. """

        self._module = QComboBox()
        layout.addWidget(self._module)

        form = QFormLayout()
        layout.addLayout(form)

        self._new_name = QLineEdit()
        form.addRow("New name", self._new_name)

    def set_fields(self):
        """ Set the dialog's fields from the project. """

        init_module_selector(self._module, self.model)

    def get_fields(self):
        """ Update the project from the dialog's fields. """

        project = self.model

        old_name = self._module.currentText()

        new_name = self._new_name.text().strip()
        if not validate_module_name(new_name, project, self):
            return False

        # Rename in the project's list.
        for module in project.modules:
            if module.name == old_name:
                module.name = new_name
                self.shell.notify(EventType.MODULE_RENAME, module)
                break
        else:
            project.externalmodules[project.externalmodules.index(old_name)] = new_name

        return True
