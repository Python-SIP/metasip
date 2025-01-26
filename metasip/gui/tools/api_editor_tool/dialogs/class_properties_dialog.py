# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2025 Phil Thompson <phil@riverbankcomputing.com>


from PyQt6.QtWidgets import (QCheckBox, QFormLayout, QGridLayout, QGroupBox,
        QLineEdit)

from ....helpers import BaseDialog

from .helpers import split_annos


class ClassPropertiesDialog(BaseDialog):
    """ This class implements the dialog for a class's properties. """

    def populate(self, layout):
        """ Populate the dialog's layout. """

        form = QFormLayout()
        layout.addLayout(form)

        self._py_bases = QLineEdit()
        form.addRow("Python base classes", self._py_bases)

        group_box = QGroupBox("Annotations")
        group_box_layout = QGridLayout()
        group_box.setLayout(group_box_layout)
        layout.addWidget(group_box)

        self._abstract = QCheckBox('Abstract')
        group_box_layout.addWidget(self._abstract, 0, 0)

        self._allow_none = QCheckBox('AllowNone')
        group_box_layout.addWidget(self._allow_none, 1, 0)

        form = QFormLayout()
        group_box_layout.addLayout(form, 2, 0)

        self._api = QLineEdit()
        form.addRow('API', self._api)

        self._delay_dtor = QCheckBox('DelayDtor')
        group_box_layout.addWidget(self._delay_dtor, 3, 0)

        self._export_derived = QCheckBox('ExportDerived')
        group_box_layout.addWidget(self._export_derived, 4, 0)

        form = QFormLayout()
        group_box_layout.addLayout(form, 5, 0)

        self._metatype = QLineEdit()
        form.addRow('Metatype', self._metatype)

        self._mixin = QCheckBox('Mixin')
        group_box_layout.addWidget(self._mixin, 6, 0)

        self._no_default_ctors = QCheckBox('NoDefaultCtors')
        group_box_layout.addWidget(self._no_default_ctors, 7, 0)

        self._no_type_hint = QCheckBox('NoTypeHint')
        group_box_layout.addWidget(self._no_type_hint, 8, 0)

        form = QFormLayout()
        group_box_layout.addLayout(form, 0, 1)

        self._py_name = QLineEdit()
        form.addRow('PyName', self._py_name)

        self._pyqt_no_qmetaobject = QCheckBox('PyQtNoQMetaObject')
        group_box_layout.addWidget(self._pyqt_no_qmetaobject, 1, 1)

        form = QFormLayout()
        group_box_layout.addLayout(form, 2, 1, 8, 1)

        self._pyqt_interface = QLineEdit()
        form.addRow('PyQtInterface', self._pyqt_interface)

        self._supertype = QLineEdit()
        form.addRow('Supertype', self._supertype)

        self._type_hint = QLineEdit()
        form.addRow('TypeHint', self._type_hint)

        self._type_hint_in = QLineEdit()
        form.addRow('TypeHintIn', self._type_hint_in)

        self._type_hint_out = QLineEdit()
        form.addRow('TypeHintOut', self._type_hint_out)

        self._type_hint_value = QLineEdit()
        form.addRow('TypeHintValue', self._type_hint_value)

    def set_fields(self):
        """ Set the dialog's fields from the API item. """

        self._py_bases.setText(self.model.pybases)

        for name, value in split_annos(self.model.annos):
            if name == 'Abstract':
                self._abstract.setChecked(True)
            elif name == 'AllowNone':
                self._allow_none.setChecked(True)
            elif name == 'DelayDtor':
                self._delay_dtor.setChecked(True)
            elif name == 'NoDefaultCtors':
                self._no_default_ctors.setChecked(True)
            elif name == 'NoTypeHint':
                self._no_type_hint.setChecked(True)
            elif name == 'PyQtNoQMetaObject':
                self._pyqt_no_qmetaobject.setChecked(True)
            elif name == 'ExportDerived':
                self._export_derived.setChecked(True)
            elif name == 'Mixin':
                self._mixin.setChecked(True)
            elif name == 'PyName':
                self._py_name.setText(value)
            elif name == 'API':
                self._api.setText(value)
            elif name == 'Metatype':
                self._metatype.setText(value)
            elif name == 'Supertype':
                self._supertype.setText(value)
            elif name == 'PyQtInterface':
                self._pyqt_interface.setText(value)
            elif name == 'TypeHint':
                self._type_hint.setText(value)
            elif name == 'TypeHintIn':
                self._type_hint_in.setText(value)
            elif name == 'TypeHintOut':
                self._type_hint_out.setText(value)
            elif name == 'TypeHintValue':
                self._type_hint_value.setText(value)

    def get_fields(self):
        """ Update the API item from the dialog's fields. """

        self.model.pybases = ' '.join(self._py_bases.text().strip().split())

        annos_list = []

        if self._abstract.isChecked():
            annos_list.append('Abstract')

        if self._allow_none.isChecked():
            annos_list.append('AllowNone')

        if self._delay_dtor.isChecked():
            annos_list.append('DelayDtor')

        if self._no_default_ctors.isChecked():
            annos_list.append('NoDefaultCtors')

        if self._no_type_hint.isChecked():
            annos_list.append('NoTypeHint')

        if self._pyqt_no_qmetaobject.isChecked():
            annos_list.append('PyQtNoQMetaObject')

        if self._export_derived.isChecked():
            annos_list.append('ExportDerived')

        if self._mixin.isChecked():
            annos_list.append('Mixin')

        py_name = self._py_name.text().strip()
        if py_name:
            annos_list.append('PyName=' + py_name)

        api = self._api.text().strip()
        if api:
            annos_list.append('API=' + api)

        metatype = self._metatype.text().strip()
        if metatype:
            annos_list.append('Metatype=' + metatype)

        supertype = self._supertype.text().strip()
        if supertype:
            annos_list.append('Supertype=' + supertype)

        type_hint = self._type_hint.text().strip()
        if type_hint:
            annos_list.append(f'TypeHint="{type_hint}"')

        type_hint_in = self._type_hint_in.text().strip()
        if type_hint_in:
            annos_list.append(f'TypeHintIn="{type_hint_in}"')

        type_hint_out = self._type_hint_out.text().strip()
        if type_hint_out:
            annos_list.append(f'TypeHintOut="{type_hint_out}"')

        type_hint_value = self._type_hint_value.text().strip()
        if type_hint_value:
            annos_list.append(f'TypeHintValue="{type_hint_value}"')

        pyqt_interface = self._pyqt_interface.text().strip()
        if pyqt_interface:
            annos_list.append('PyQtInterface=' + pyqt_interface)

        self.model.annos = ','.join(annos_list)

        return True
