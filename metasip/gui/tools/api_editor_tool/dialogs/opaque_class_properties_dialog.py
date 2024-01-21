# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


from PyQt6.QtWidgets import QCheckBox, QGroupBox, QVBoxLayout

from ....helpers import BaseDialog

from .helpers import split_annos


class OpaqueClassPropertiesDialog(BaseDialog):
    """ This class implements the dialog for an opaque class's properties. """

    def populate(self, layout):
        """ Populate the dialog's layout. """

        group_box = QGroupBox("Annotations")
        group_box_layout = QVBoxLayout()
        group_box.setLayout(group_box_layout)
        layout.addWidget(group_box)

        self._external = QCheckBox('External')
        group_box_layout.addWidget(self._external)

    def set_fields(self):
        """ Set the dialog's fields from the API item. """

        for name, value in split_annos(self.model.annos):
            if name == 'External':
                self._external.setChecked(True)

    def get_fields(self):
        """ Update the API item from the dialog's fields. """

        annos_list = []

        if self._external.isChecked():
            annos_list.append('External')

        self.model.annos = ','.join(annos_list)

        return True
