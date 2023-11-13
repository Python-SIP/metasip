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


from PyQt6.QtWidgets import QCheckBox, QGroupBox, QVBoxLayout

from .base_dialog import BaseDialog
from .helpers import split_annos


class OpaqueClassPropertiesDialog(BaseDialog):
    """ This class implements the dialog for an opaque class's properties. """

    def populate(self):
        """ Populate the dialog's layout. """

        layout = self.layout()

        group_box = QGroupBox("Annotations")
        group_box_layout = QVBoxLayout()
        group_box.setLayout(group_box_layout)
        layout.addWidget(group_box)

        self._external = QCheckBox('External')
        group_box_layout.addWidget(self._external)

    def set_fields(self):
        """ Set the dialog's fields from the API item. """

        for name, value in split_annos(self.api_item.annos):
            if name == 'External':
                self._external.setChecked(True)

    def get_fields(self):
        """ Update the API item from the dialog's fields. """

        annos_list = []

        if self._external.isChecked():
            annos_list.append('External')

        self.api_item.annos = ','.join(annos_list)
