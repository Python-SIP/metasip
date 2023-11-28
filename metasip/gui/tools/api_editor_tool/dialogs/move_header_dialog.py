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


from PyQt6.QtWidgets import QComboBox, QDialog, QFormLayout

from ....helpers import BaseDialog


class MoveHeaderDialog(BaseDialog):
    """ This class implements the dialog for moving a header file to another
    module.
    """

    def populate(self, layout):
        """ Populate the dialog's layout. """

        project = self.shell.project

        form = QFormLayout()
        layout.addLayout(form)

        self._dst_module = QComboBox()
        form.addRow("Destination module", self._dst_module)

        for module in sorted(project.modules, key=lambda m: m.name):
            if module is not self.model:
                self._dst_module.addItem(module.name, module)

    def get_destination_module(self):
        """ Return the destination module or None if the dialog was cancelled.
        """

        if self.dialog.exec() == int(QDialog.DialogCode.Rejected):
            return None

        return self._dst_module.currentData()
