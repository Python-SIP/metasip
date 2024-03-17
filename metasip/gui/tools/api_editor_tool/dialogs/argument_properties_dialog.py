# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


from PyQt6.QtWidgets import (QCheckBox, QComboBox, QFormLayout, QGridLayout,
        QGroupBox, QHBoxLayout, QLabel, QLineEdit)

from ....helpers import BaseDialog

from .helpers import Encoding, split_annos


class ArgumentPropertiesDialog(BaseDialog):
    """ This class implements the dialog for argument properties. """

    def populate(self, layout):
        """ Populate the dialog's layout. """

        name_layout = QHBoxLayout()
        layout.addLayout(name_layout)

        name_layout.addWidget(QLabel("Name"))
        self._name = QLineEdit()
        name_layout.addWidget(self._name)
        self._unnamed = QCheckBox("Unnamed")
        name_layout.addWidget(self._unnamed)

        form = QFormLayout()
        layout.addLayout(form)

        self._py_type = QLineEdit()
        form.addRow("Python type", self._py_type)

        self._py_default = QLineEdit()
        form.addRow("Python default value", self._py_default)

        group_box = QGroupBox("Annotations")
        layout.addWidget(group_box)
        group_box_layout = QGridLayout()
        group_box.setLayout(group_box_layout)

        self._allow_none = QCheckBox('AllowNone')
        group_box_layout.addWidget(self._allow_none, 0, 0)

        self._array = QCheckBox('Array')
        group_box_layout.addWidget(self._array, 1, 0)

        self._array_size = QCheckBox('ArraySize')
        group_box_layout.addWidget(self._array_size, 2, 0)

        self._constrained = QCheckBox('Constrained')
        group_box_layout.addWidget(self._constrained, 3, 0)

        self._disallow_none = QCheckBox('DisallowNone')
        group_box_layout.addWidget(self._disallow_none, 4, 0)

        form = QFormLayout()
        group_box_layout.addLayout(form, 5, 0, 4, 1)

        self._doc_type = QLineEdit()
        form.addRow('DocType', self._doc_type)

        self._doc_value = QLineEdit()
        form.addRow('DocValue', self._doc_value)

        self._doc_type = QLineEdit()
        form.addRow('DocType', self._doc_type)

        encoding = QComboBox()
        form.addRow('Encoding', encoding)
        self._encoding_helper = Encoding(encoding)

        self._get_wrapper = QCheckBox('GetWrapper')
        group_box_layout.addWidget(self._get_wrapper, 9, 0)

        self._in = QCheckBox('In')
        group_box_layout.addWidget(self._in, 10, 0)

        self._keep_reference = QCheckBox('KeepReference')
        group_box_layout.addWidget(self._keep_reference, 11, 0)
        self._keep_reference.stateChanged.connect(self._update_reference)

        self._no_copy = QCheckBox('NoCopy')
        group_box_layout.addWidget(self._no_copy, 12, 0)

        self._out = QCheckBox('Out')
        group_box_layout.addWidget(self._out, 0, 1)

        self._py_int = QCheckBox('PyInt')
        group_box_layout.addWidget(self._py_int, 1, 1)

        form = QFormLayout()
        group_box_layout.addLayout(form, 2, 1)

        self._reference_label = QLabel('Reference')
        self._reference = QLineEdit()
        form.addRow(self._reference_label, self._reference)

        self._result_size = QCheckBox('ResultSize')
        group_box_layout.addWidget(self._result_size, 3, 1)

        form = QFormLayout()
        group_box_layout.addLayout(form, 4, 1)

        self._scopes_stripped = QLineEdit()
        form.addRow('ScopesStripped', self._scopes_stripped)

        self._single_shot = QCheckBox('SingleShot')
        group_box_layout.addWidget(self._single_shot, 5, 1)

        self._transfer = QCheckBox('Transfer')
        group_box_layout.addWidget(self._transfer, 6, 1)

        self._transfer_back = QCheckBox('TransferBack')
        group_box_layout.addWidget(self._transfer_back, 7, 1)

        self._transfer_this = QCheckBox('TransferThis')
        group_box_layout.addWidget(self._transfer_this, 8, 1)

        form = QFormLayout()
        group_box_layout.addLayout(form, 9, 1, 4, 1)

        self._type_hint = QLineEdit()
        form.addRow('TypeHint', self._type_hint)

        self._type_hint_in = QLineEdit()
        form.addRow('TypeHintIn', self._type_hint_in)

        self._type_hint_out = QLineEdit()
        form.addRow('TypeHintOut', self._type_hint_out)

    def set_fields(self):
        """ Set the dialog's fields from the API item. """

        self._name.setText(self.model.name)
        self._unnamed.setChecked(self.model.unnamed)
        self._py_type.setText(self.model.pytype)
        self._py_default.setText(self.model.pydefault)

        for name, value in split_annos(self.model.annos):
            if name == 'AllowNone':
                self._allow_none.setChecked(True)
            elif name == 'Array':
                self._array.setChecked(True)
            elif name == 'ArraySize':
                self._array_size.setChecked(True)
            elif name == 'Constrained':
                self._constrained.setChecked(True)
            elif name == 'DisallowNone':
                self._disallow_none.setChecked(True)
            elif name == 'DocType':
                self._doc_type.setText(value)
            elif name == 'DocValue':
                self._doc_value.setText(value)
            elif name == 'Encoding':
                self._encoding_helper.setAnnotation(value)
            elif name == 'GetWrapper':
                self._get_wrapper.setChecked(True)
            elif name == 'In':
                self._in.setChecked(True)
            elif name == 'KeepReference':
                self._keep_reference.setChecked(True)

                if value is not None:
                    self._reference.setText(value)
            elif name == 'NoCopy':
                self._no_copy.setChecked(True)
            elif name == 'Out':
                self._out.setChecked(True)
            elif name == 'PyInt':
                self._py_int.setChecked(True)
            elif name == 'ResultSize':
                self._result_size.setChecked(True)
            elif name == 'SingleShot':
                self._single_shot.setChecked(True)
            elif name == 'ScopesStripped':
                self._scopes_stripped.setText(value)
            elif name == 'Transfer':
                self._transfer.setChecked(True)
            elif name == 'TransferBack':
                self._transfer_back.setChecked(True)
            elif name == 'TransferThis':
                self._transfer_this.setChecked(True)
            elif name == 'TypeHint':
                self._type_hint.setText(value)
            elif name == 'TypeHintIn':
                self._type_hint_in.setText(value)
            elif name == 'TypeHintOut':
                self._type_hint_out.setText(value)

        self._update_reference()

    def get_fields(self):
        """ Update the API item from the dialog's field. """

        self.model.name = self._name.text().strip()
        self.model.unnamed = self._unnamed.isChecked()
        self.model.pytype = self._py_type.text().strip()
        self.model.pydefault = self._py_default.text().strip()

        annos_list = []

        if self._allow_none.isChecked():
            annos_list.append('AllowNone')

        if self._array.isChecked():
            annos_list.append('Array')

        if self._array_size.isChecked():
            annos_list.append('ArraySize')

        if self._constrained.isChecked():
            annos_list.append('Constrained')

        if self._disallow_none.isChecked():
            annos_list.append('DisallowNone')

        doc_type = self._doc_type.text().strip()
        if doc_type:
            annos_list.append(f'DocType="{doc_type}"')

        doc_value = self._doc_value.text().strip()
        if doc_value:
            annos_list.append(f'DocValue="{doc_value}"')

        self._encoding_helper.annotation(annos_list)

        if self._get_wrapper.isChecked():
            annos_list.append('GetWrapper')

        if self._in.isChecked():
            annos_list.append('In')

        if self._keep_reference.isChecked():
            reference = self._reference.text().strip()
            if reference:
                annos_list.append('KeepReference=' + reference)
            else:
                annos_list.append('KeepReference')

        if self._no_copy.isChecked():
            annos_list.append('NoCopy')

        if self._out.isChecked():
            annos_list.append('Out')

        if self._py_int.isChecked():
            annos_list.append('PyInt')

        if self._result_size.isChecked():
            annos_list.append('ResultSize')

        if self._single_shot.isChecked():
            annos_list.append('SingleShot')

        scopes_stripped = self._scopes_stripped.text().strip()
        if scopes_stripped:
            annos_list.append('ScopesStripped=' + scopes_stripped)

        if self._transfer.isChecked():
            annos_list.append('Transfer')

        if self._transfer_back.isChecked():
            annos_list.append('TransferBack')

        if self._transfer_this.isChecked():
            annos_list.append('TransferThis')

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

    def _update_reference(self, state=None):
        """ Enable the reference field if the keep reference field is checked.
        """

        checked = self._keep_reference.isChecked()

        self._reference_label.setEnabled(checked)
        self._reference.setEnabled(checked)
