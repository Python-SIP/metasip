# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2025 Phil Thompson <phil@riverbankcomputing.com>


from PyQt6.QtWidgets import (QCheckBox, QFormLayout, QGroupBox, QLineEdit,
        QVBoxLayout)

from ....helpers import BaseDialog

from .helpers import split_annos


class EnumMemberPropertiesDialog(BaseDialog):
    """ This class implements the dialog for an enum member's properties. """

    def populate(self, layout):
        """ Populate the dialog's layout. """

        group_box = QGroupBox("Annotations")
        group_box_layout = QVBoxLayout()
        group_box.setLayout(group_box_layout)
        layout.addWidget(group_box)

        self._no_type_hint = QCheckBox('NoTypeHint')
        group_box_layout.addWidget(self._no_type_hint)

        form = QFormLayout()
        group_box_layout.addLayout(form)

        self._py_name = QLineEdit()
        form.addRow('PyName', self._py_name)

    def set_fields(self):
        """ Set the dialog's fields from the API item. """

        for name, value in split_annos(self.model.annos):
            if name == 'NoTypeHint':
                self._no_type_hint.setChecked(True)
            elif name == 'PyName':
                self._py_name.setText(value)

    def get_fields(self):
        """ Update the API item from the dialog's fields. """

        annos_list = []

        if self._no_type_hint.isChecked():
            annos_list.append('NoTypeHint')

        py_name = self._py_name.text().strip()
        if py_name:
            annos_list.append('PyName=' + py_name)

        self.model.annos = ','.join(annos_list)

        return True
