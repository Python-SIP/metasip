# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


from PyQt6.QtWidgets import (QCheckBox, QComboBox, QFormLayout, QGroupBox,
        QLineEdit, QVBoxLayout)

from ....helpers import BaseDialog

from .helpers import Encoding, split_annos


class TypedefPropertiesDialog(BaseDialog):
    """ This class implements the dialog for a typedef's properties. """

    def populate(self, layout):
        """ Populate the dialog's layout. """

        group_box = QGroupBox("Annotations")
        layout.addWidget(group_box)
        group_box_layout = QVBoxLayout()
        group_box.setLayout(group_box_layout)

        self._capsule = QCheckBox('Capsule')
        group_box_layout.addWidget(self._capsule)

        form = QFormLayout()
        group_box_layout.addLayout(form)

        encoding = QComboBox()
        self._encoding_helper = Encoding(encoding)
        form.addRow('Encoding', encoding)

        self._no_type_name = QCheckBox('NoTypeName')
        group_box_layout.addWidget(self._no_type_name)

        self._py_int = QCheckBox('PyInt')
        group_box_layout.addWidget(self._py_int)

        form = QFormLayout()
        group_box_layout.addLayout(form)

        self._py_name = QLineEdit()
        form.addRow('PyName', self._py_name)

        self._type_hint = QLineEdit()
        form.addRow('TypeHint', self._type_hint)

        self._type_hint_in = QLineEdit()
        form.addRow('TypeHintIn', self._type_hint_in)

        self._type_hint_out = QLineEdit()
        form.addRow('TypeHintOut', self._type_hint_out)

    def set_fields(self):
        """ Set the dialog's fields from the API item. """

        for name, value in split_annos(self.model.annos):
            if name == 'Capsule':
                self._capsule.setChecked(True)
            elif name == 'Encoding':
                self._encoding_helper.setAnnotation(value)
            elif name == 'NoTypeName':
                self._no_type_name.setChecked(True)
            elif name == 'PyInt':
                self._py_int.setChecked(True)
            elif name == 'PyName':
                self._py_name.setText(value)
            elif name == 'TypeHint':
                self._type_hint.setText(value)
            elif name == 'TypeHintIn':
                self._type_hint_in.setText(value)
            elif name == 'TypeHintOut':
                self._type_hint_out.setText(value)

    def get_fields(self):
        """ Update the API item from the dialog's fields. """

        annos_list = []

        self._encoding_helper.annotation(annos_list)

        if self._capsule.isChecked():
            annos_list.append('Capsule')

        if self._no_type_name.isChecked():
            annos_list.append('NoTypeName')

        if self._py_int.isChecked():
            annos_list.append('PyInt')

        py_name = self._py_name.text().strip()
        if py_name:
            annos_list.append('PyName=' + py_name)

        type_hint = self._type_hint.text().strip()
        if type_hint:
            annos_list.append(f'TypeHint="{type_hint}"')

        type_hint_in = self._type_hint_in.text().strip()
        if type_hint_in:
            annos_list.append(f'TypeHintIn="{type_hint_in}"')

        type_hint_out = self._type_hint_out.text().strip()
        if type_hint_out:
            annos_list.append(f'TypeHintOut="{type_hint_out}"')

        self.model.annos = ','.join(annos_list)

        return True
