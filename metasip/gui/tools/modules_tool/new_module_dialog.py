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


from PyQt6.QtWidgets import QCheckBox, QFormLayout, QLineEdit

from ....project import Module

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
            project.modules.append(Module(name=module_name))

        self.shell.notify(EventType.MODULE_ADD_DELETE)

        return True
