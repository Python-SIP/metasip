# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


from PyQt6.QtWidgets import (QCheckBox, QComboBox, QFormLayout, QGroupBox,
        QLineEdit, QVBoxLayout)

from ....helpers import BaseDialog

from .helpers import BaseType, split_annos


class EnumPropertiesDialog(BaseDialog):
    """ This class implements the dialog for an enum's properties. """

    def populate(self, layout):
        """ Populate the dialog's layout. """

        group_box = QGroupBox("Annotations")
        group_box_layout = QVBoxLayout()
        group_box.setLayout(group_box_layout)
        layout.addWidget(group_box)

        form = QFormLayout()
        group_box_layout.addLayout(form)

        self._py_name = QLineEdit()
        form.addRow('PyName', self._py_name)

        base_type = QComboBox()
        form.addRow('BaseType', base_type)
        self._base_type_helper = BaseType(base_type)

        self._no_scope = QCheckBox('NoScope')
        group_box_layout.addWidget(self._no_scope)

        self._no_type_hint = QCheckBox('NoTypeHint')
        group_box_layout.addWidget(self._no_type_hint)

    def set_fields(self):
        """ Set the dialog's fields from the API item. """

        for name, value in split_annos(self.model.annos):
            if name == 'PyName':
                self._py_name.setText(value)
            elif name == 'BaseType':
                self._base_type_helper.setAnnotation(value)
            elif name == 'NoScope':
                self._no_scope.setChecked(True)
            elif name == 'NoTypeHint':
                self._no_type_hint.setChecked(True)

    def get_fields(self):
        """ Update the API item from the dialog's fields. """

        annos_list = []

        self._base_type_helper.annotation(annos_list)

        s = self._py_name.text().strip()
        if s != '':
            annos_list.append('PyName=' + s)

        if self._no_scope.isChecked():
            annos_list.append('NoScope')

        if self._no_type_hint.isChecked():
            annos_list.append('NoTypeHint')

        self.model.annos = ','.join(annos_list)

        return True
