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
            annos_list.append('PyName=' + s)

        self.model.annos = ','.join(annos_list)

        return True
