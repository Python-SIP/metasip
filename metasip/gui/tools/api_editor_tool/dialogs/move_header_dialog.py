# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


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

        if self.widget.exec() == int(QDialog.DialogCode.Rejected):
            return None

        return self._dst_module.currentData()
