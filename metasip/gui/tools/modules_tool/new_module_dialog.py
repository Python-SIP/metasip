# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2025 Phil Thompson <phil@riverbankcomputing.com>


from PyQt6.QtWidgets import QCheckBox, QFormLayout, QLineEdit

from ....models import Module

from ...helpers import BaseDialog
from ...shell import EventType

from .helpers import validate_module_name


class NewModuleDialog(BaseDialog):
    """ This class implements the dialog for creating a new module. """

    def populate(self, layout):
        """ Populate the dialog's layout. """

        form = QFormLayout()
        layout.addLayout(form)

        self._module = QLineEdit()
        form.addRow("Module name", self._module)

        self._external = QCheckBox("Module is defined in another project?")
        layout.addWidget(self._external)

    def get_fields(self):
        """ Update the project from the dialog's fields. """

        project = self.model

        module_name = self._module.text().strip()
        if not validate_module_name(module_name, project, self):
            return False

        if self._external.isChecked():
            project.externalmodules.append(module_name)
        else:
            module = Module(name=module_name)
            project.modules.append(module)
            self.shell.notify(EventType.MODULE_ADD, module)

        return True
