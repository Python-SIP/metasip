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


from PyQt6.QtWidgets import QFormLayout, QLineEdit

from ....helpers import AbstractDialog


class ManualCodeDialog(AbstractDialog):
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
