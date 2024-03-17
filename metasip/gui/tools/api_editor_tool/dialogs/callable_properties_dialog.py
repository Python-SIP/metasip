# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


from PyQt6.QtWidgets import (QCheckBox, QComboBox, QFormLayout, QGridLayout,
        QGroupBox, QLineEdit)

from .....models import (Constructor, Destructor, Method, OperatorMethod,
        Function, OperatorFunction, ManualCode)

from ....helpers import BaseDialog

from .helpers import Encoding, split_annos


class CallablePropertiesDialog(BaseDialog):
    """ This class implements the dialog for callable properties. """

    def populate(self, layout):
        """ Populate the dialog's layout. """

        form = QFormLayout()
        layout.addLayout(form)

        self._py_type = QLineEdit()
        form.addRow("Python return type", self._py_type)

        self._py_args = QLineEdit()
        form.addRow("Python arguments", self._py_args)

        group_box = QGroupBox("Annotations")
        layout.addWidget(group_box)
        group_box_layout = QGridLayout()
        group_box.setLayout(group_box_layout)

        self._abort_on_exception = QCheckBox('AbortOnException')
        group_box_layout.addWidget(self._abort_on_exception, 0, 0)

        self._allow_none = QCheckBox('AllowNone')
        group_box_layout.addWidget(self._allow_none, 1, 0)

        form = QFormLayout()
        group_box_layout.addLayout(form, 2, 0)

        self._api = QLineEdit()
        form.addRow('API', self._api)

        self._auto_gen = QLineEdit()
        form.addRow('AutoGen', self._auto_gen)

        self._default = QCheckBox('Default')
        group_box_layout.addWidget(self._default, 3, 0)

        self._disallow_none = QCheckBox('DisallowNone')
        group_box_layout.addWidget(self._disallow_none, 4, 0)

        form = QFormLayout()
        group_box_layout.addLayout(form, 5, 0, 2, 1)

        self._doc_type = QLineEdit()
        form.addRow('DocType', self._doc_type)

        self._encoding = QComboBox()
        form.addRow('Encoding', self._encoding)
        self._encoding_helper = Encoding(self._encoding)

        self._factory = QCheckBox('Factory')
        group_box_layout.addWidget(self._factory, 7, 0)

        # Note that 'final' isn't actually an annotation.
        self._final = QCheckBox('final')
        group_box_layout.addWidget(self._final, 8, 0)

        self._hold_gil = QCheckBox('HoldGIL')
        group_box_layout.addWidget(self._hold_gil, 9, 0)

        self._keep_reference = QCheckBox('KeepReference')
        group_box_layout.addWidget(self._keep_reference, 10, 0)

        self._new_thread = QCheckBox('NewThread')
        group_box_layout.addWidget(self._new_thread, 11, 0)

        self._no_arg_parser = QCheckBox('NoArgParser')
        group_box_layout.addWidget(self._no_arg_parser, 12, 0)

        self._no_copy = QCheckBox('NoCopy')
        group_box_layout.addWidget(self._no_copy, 13, 0)

        self._no_derived = QCheckBox('NoDerived')
        group_box_layout.addWidget(self._no_derived, 14, 0)

        self._no_type_hint = QCheckBox('NoTypeHint')
        group_box_layout.addWidget(self._no_type_hint, 0, 1)

        self._numeric = QCheckBox('Numeric')
        group_box_layout.addWidget(self._numeric, 1, 1)

        form = QFormLayout()
        group_box_layout.addLayout(form, 2, 1, 4, 1)

        self._post_hook = QLineEdit()
        form.addRow('PostHook', self._post_hook)

        self._pre_hook = QLineEdit()
        form.addRow('PreHook', self._pre_hook)

        self._py_name = QLineEdit()
        form.addRow('PyName', self._py_name)

        self._pyqt_signal_hack = QLineEdit()
        form.addRow('PyQtSignalHack', self._pyqt_signal_hack)

        self._py_int = QCheckBox('PyInt')
        group_box_layout.addWidget(self._py_int, 6, 1)

        self._release_gil = QCheckBox('ReleaseGIL')
        group_box_layout.addWidget(self._release_gil, 7, 1)

        self._transfer = QCheckBox('Transfer')
        group_box_layout.addWidget(self._transfer, 8, 1)

        self._transfer_back = QCheckBox('TransferBack')
        group_box_layout.addWidget(self._transfer_back, 9, 1)

        self._transfer_this = QCheckBox('TransferThis')
        group_box_layout.addWidget(self._transfer_this, 10, 1)

        form = QFormLayout()
        group_box_layout.addLayout(form, 11, 1)

        self._type_hint = QLineEdit()
        form.addRow('TypeHint', self._type_hint)

        self._len = QCheckBox('__len__')
        group_box_layout.addWidget(self._len, 12, 1)

        self._matmul = QCheckBox('__matmul__')
        group_box_layout.addWidget(self._matmul, 13, 1)

        self._imatmul = QCheckBox('__imatmul__')
        group_box_layout.addWidget(self._imatmul, 14, 1)

        if isinstance(self.model, Constructor):
            self.widget.setWindowTitle("Constructor Properties")

            self._py_type.setEnabled(False)
            self._abort_on_exception.setEnabled(False)
            self._allow_none.setEnabled(False)
            self._auto_gen.setEnabled(False)
            self._disallow_none.setEnabled(False)
            self._doc_type.setEnabled(False)
            self._encoding.setEnabled(False)
            self._factory.setEnabled(False)
            self._final.setEnabled(False)
            self._keep_reference.setEnabled(False)
            self._len.setEnabled(False)
            self._matmul.setEnabled(False)
            self._imatmul.setEnabled(False)
            self._new_thread.setEnabled(False)
            self._no_arg_parser.setEnabled(False)
            self._no_copy.setEnabled(False)
            self._numeric.setEnabled(False)
            self._py_int.setEnabled(False)
            self._transfer_back.setEnabled(False)
            self._transfer_this.setEnabled(False)
            self._py_name.setEnabled(False)
            self._type_hint.setEnabled(False)

        elif isinstance(self.model, Destructor):
            self.widget.setWindowTitle("Destructor Properties")

            self._py_type.setEnabled(False)
            self._py_args.setEnabled(False)
            self._abort_on_exception.setEnabled(False)
            self._allow_none.setEnabled(False)
            self._api.setEnabled(False)
            self._auto_gen.setEnabled(False)
            self._default.setEnabled(False)
            self._disallow_none.setEnabled(False)
            self._doc_type.setEnabled(False)
            self._encoding.setEnabled(False)
            self._factory.setEnabled(False)
            self._final.setEnabled(False)
            self._keep_reference.setEnabled(False)
            self._len.setEnabled(False)
            self._matmul.setEnabled(False)
            self._imatmul.setEnabled(False)
            self._new_thread.setEnabled(False)
            self._no_arg_parser.setEnabled(False)
            self._no_copy.setEnabled(False)
            self._no_derived.setEnabled(False)
            self._numeric.setEnabled(False)
            self._post_hook.setEnabled(False)
            self._pre_hook.setEnabled(False)
            self._py_int.setEnabled(False)
            self._transfer.setEnabled(False)
            self._transfer_back.setEnabled(False)
            self._transfer_this.setEnabled(False)
            self._py_name.setEnabled(False)
            self._type_hint.setEnabled(False)

        elif isinstance(self.model, Method):
            self.widget.setWindowTitle("Method Properties")

            self._default.setEnabled(False)
            self._no_derived.setEnabled(False)

        elif isinstance(self.model, OperatorMethod):
            self.widget.setWindowTitle("Operator Method Properties")

            self._abort_on_exception.setEnabled(False)
            self._default.setEnabled(False)
            self._final.setEnabled(False)
            self._keep_reference.setEnabled(False)
            self._len.setEnabled(False)
            self._matmul.setEnabled(False)
            self._imatmul.setEnabled(False)
            self._no_arg_parser.setEnabled(False)
            self._no_derived.setEnabled(False)
            self._py_name.setEnabled(False)

        elif isinstance(self.model, Function):
            self.widget.setWindowTitle("Function Properties")

            self._abort_on_exception.setEnabled(False)
            self._default.setEnabled(False)
            self._final.setEnabled(False)
            self._keep_reference.setEnabled(False)
            self._len.setEnabled(False)
            self._matmul.setEnabled(False)
            self._imatmul.setEnabled(False)
            self._no_copy.setEnabled(False)
            self._no_derived.setEnabled(False)
            self._transfer.setEnabled(False)
            self._transfer_this.setEnabled(False)

        elif isinstance(self.model, OperatorFunction):
            self.widget.setWindowTitle("Operator Function Properties")

            self._abort_on_exception.setEnabled(False)
            self._default.setEnabled(False)
            self._final.setEnabled(False)
            self._keep_reference.setEnabled(False)
            self._len.setEnabled(False)
            self._matmul.setEnabled(False)
            self._imatmul.setEnabled(False)
            self._no_arg_parser.setEnabled(False)
            self._no_copy.setEnabled(False)
            self._no_derived.setEnabled(False)
            self._transfer.setEnabled(False)
            self._transfer_this.setEnabled(False)
            self._py_name.setEnabled(False)

        elif isinstance(self.model, ManualCode):
            self.widget.setWindowTitle("Manual Code Properties")

            self._py_type.setEnabled(False)
            self._py_args.setEnabled(False)
            self._py_name.setEnabled(False)

    def set_fields(self):
        """ Set the dialog's fields from the API item. """

        if isinstance(self.model, Constructor):
            self._py_args.setText(self.model.pyargs)

        elif isinstance(self.model, Method):
            self._py_type.setText(self.model.pytype)
            self._py_args.setText(self.model.pyargs)
            self._final.setChecked(self.model.final)

        elif isinstance(self.model, (OperatorMethod, Function, OperatorFunction)):
            self._py_type.setText(self.model.pytype)
            self._py_args.setText(self.model.pyargs)

        for name, value in split_annos(self.model.annos):
            if name == 'AbortOnException':
                self._abort_on_exception.setChecked(True)
            elif name == 'AllowNone':
                self._allow_none.setChecked(True)
            elif name == 'API':
                self._api.setText(value)
            elif name == 'AutoGen':
                if value is None:
                    value = 'All'

                self._auto_gen.setText(value)
            elif name == 'Default':
                self._default.setChecked(True)
            elif name == 'DisallowNone':
                self._disallow_none.setChecked(True)
            elif name == 'DocType':
                self._doc_type.setText(value)
            elif name == 'Encoding':
                self._encoding_helper.setAnnotation(value)
            elif name == 'Factory':
                self._factory.setChecked(True)
            elif name == 'HoldGIL':
                self._hold_gil.setChecked(True)
            elif name == 'KeepReference':
                self._keep_reference.setChecked(True)
            elif name == '__len__':
                self._len.setChecked(True)
            elif name == '__matmul__':
                self._matmul.setChecked(True)
            elif name == '__imatmul__':
                self._imatmul.setChecked(True)
            elif name == 'NewThread':
                self._new_thread.setChecked(True)
            elif name == 'NoArgParser':
                self._no_arg_parser.setChecked(True)
            elif name == 'NoCopy':
                self._no_copy.setChecked(True)
            elif name == 'NoDerived':
                self._no_derived.setChecked(True)
            elif name == 'NoTypeHint':
                self._no_type_hint.setChecked(True)
            elif name == 'Numeric':
                self._numeric.setChecked(True)
            elif name == 'PostHook':
                self._post_hook.setText(value)
            elif name == 'PreHook':
                self._pre_hook.setText(value)
            elif name == 'PyInt':
                self._py_int.setChecked(True)
            elif name == 'PyName':
                self._py_name.setText(value)
            elif name == 'PyQtSignalHack':
                self._pyqt_signal_hack.setText(value)
            elif name == 'ReleaseGIL':
                self._release_gil.setChecked(True)
            elif name == 'Transfer':
                self._transfer.setChecked(True)
            elif name == 'TransferBack':
                self._transfer_back.setChecked(True)
            elif name == 'TransferThis':
                self._transfer_this.setChecked(True)
            elif name == 'TypeHint':
                self._type_hint.setText(value)

    def get_fields(self):
        """ Update the API item from the dialog's fields. """

        if hasattr(self.model, 'pytype') and self.model.pytype is not None:
            self.model.pytype = self._py_type.text().strip()

        if hasattr(self.model, 'pyargs'):
            self.model.pyargs = self._py_args.text().strip()

        if hasattr(self.model, 'final'):
            self.model.final = self._final.isChecked()

        annos_list = []

        if self._abort_on_exception.isChecked():
            annos_list.append('AbortOnException')

        if self._allow_none.isChecked():
            annos_list.append('AllowNone')

        api = self._api.text().strip()
        if api:
            annos_list.append('API=' + api)

        auto_gen = self._auto_gen.text().strip()
        if auto_gen:
            if auto_gen == 'All':
                annos_list.append('AutoGen')
            else:
                annos_list.append('AutoGen=' + auto_gen)

        if self._default.isChecked():
            annos_list.append('Default')

        if self._disallow_none.isChecked():
            annos_list.append('DisallowNone')

        doc_type = self._doc_type.text().strip()
        if doc_type:
            annos_list.append(f'DocType="{doc_type}"')

        self._encoding_helper.annotation(annos_list)

        if self._factory.isChecked():
            annos_list.append('Factory')

        if self._hold_gil.isChecked():
            annos_list.append('HoldGIL')

        if self._keep_reference.isChecked():
            annos_list.append('KeepReference')

        if self._len.isChecked():
            annos_list.append('__len__')

        if self._matmul.isChecked():
            annos_list.append('__matmul__')

        if self._imatmul.isChecked():
            annos_list.append('__imatmul__')

        if self._new_thread.isChecked():
            annos_list.append('NewThread')

        if self._no_arg_parser.isChecked():
            annos_list.append('NoArgParser')

        if self._no_copy.isChecked():
            annos_list.append('NoCopy')

        if self._no_derived.isChecked():
            annos_list.append('NoDerived')

        if self._no_type_hint.isChecked():
            annos_list.append('NoTypeHint')

        if self._numeric.isChecked():
            annos_list.append('Numeric')

        post_hook = self._post_hook.text().strip()
        if post_hook:
            annos_list.append('PostHook=' + post_hook)

        pre_hook = self._pre_hook.text().strip()
        if pre_hook:
            annos_list.append('PreHook=' + pre_hook)

        if self._py_int.isChecked():
            annos_list.append('PyInt')

        py_name = self._py_name.text().strip()
        if py_name:
            annos_list.append('PyName=' + py_name)

        pyqt_signal_hack = self._pyqt_signal_hack.text().strip()
        if pyqt_signal_hack:
            annos_list.append('PyQtSignalHack=' + pyqt_signal_hack)

        if self._release_gil.isChecked():
            annos_list.append('ReleaseGIL')

        if self._transfer.isChecked():
            annos_list.append('Transfer')

        if self._transfer_back.isChecked():
            annos_list.append('TransferBack')

        if self._transfer_this.isChecked():
            annos_list.append('TransferThis')

        type_hint = self._type_hint.text().strip()
        if type_hint:
            annos_list.append(f'TypeHint="{type_hint}"')

        self.model.annos = ','.join(annos_list)

        return True
