# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


from PyQt6.QtWidgets import QFormLayout, QLineEdit

from ....helpers import BaseDialog


class ManualCodeDialog(BaseDialog):
    """ This class implements the dialog for manual code. """

    def populate(self, layout):
        """ Populate the dialog's layout. """

        form = QFormLayout()
        layout.addLayout(form)

        self._precis = QLineEdit()
        form.addRow("Precis", self._precis)

    def set_fields(self):
        """ Set the dialog's fields from the API item. """

        self._precis.setText(self.model.precis)

    def get_fields(self):
        """ Update the API item from the dialog's fields. """

        self.model.precis = self._precis.text().strip()

        return True
