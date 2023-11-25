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


from PyQt6.QtWidgets import QComboBox, QFormLayout, QLineEdit

from ...helpers import AbstractDialog

from ..helpers import tagged_items

from .helpers import init_module_selector, validate_module_name


class RenameModuleDialog(AbstractDialog):
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
        # TODO - this should probably generate a lot more events.
        for module in project.modules:
            if module.name == old_name:
                module.name = new_name
                break
        else:
            project.externalmodules[project.externalmodules.index(old_name)] = new_name

        return True
