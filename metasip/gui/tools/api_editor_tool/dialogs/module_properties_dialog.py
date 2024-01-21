# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


from PyQt6.QtWidgets import (QCheckBox, QComboBox, QFormLayout, QGridLayout,
        QGroupBox, QLineEdit, QPlainTextEdit)

from ....helpers import BaseDialog


class ModulePropertiesDialog(BaseDialog):
    """ This class implements the dialog for a module's properties. """

    def populate(self, layout):
        """ Populate the dialog's layout. """

        project = self.shell.project

        self._all_imports = list(project.externalmodules)
        self._all_imports.extend([m.name for m in project.modules])
        self._all_imports.sort()

        form = QFormLayout()
        layout.addLayout(form)

        self._output_dir_suffix = QLineEdit()
        form.addRow("Output directory suffix", self._output_dir_suffix)

        self._directives = QPlainTextEdit()
        self._directives.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        form.addRow("Addional directives", self._directives)

        self._call_super_init = QComboBox()
        self._call_super_init.addItems(("Undefined", "No", "Yes"))
        form.addRow("Call super().__init__()", self._call_super_init)

        self._virtual_error_handler = QLineEdit()
        form.addRow("Default virtual error handler",
                self._virtual_error_handler)

        self._py_ssizet_clean = QCheckBox("#define PY_SSIZE_T_CLEAN")
        layout.addWidget(self._py_ssizet_clean)

        self._use_limited_api = QCheckBox("Use the limited Python API")
        layout.addWidget(self._use_limited_api)

        group_box = QGroupBox("%Import")
        layout.addWidget(group_box)
        self._imports_layout = QGridLayout()
        group_box.setLayout(self._imports_layout)

        for i, module in enumerate(self._all_imports):
            self._imports_layout.addWidget(QCheckBox(module), i // 2, i % 2)

    def set_fields(self):
        """ Set the dialog's fields from the API item. """

        self._output_dir_suffix.setText(self.model.outputdirsuffix)
        self._directives.setPlainText(self.model.directives)

        if self.model.callsuperinit == 'undefined':
            idx = 0
        elif self.model.callsuperinit == 'no':
            idx = 1
        else:
            idx = 2

        self._call_super_init.setCurrentIndex(idx)

        self._virtual_error_handler.setText(self.model.virtualerrorhandler)
        self._use_limited_api.setChecked(self.model.uselimitedapi)
        self._py_ssizet_clean.setChecked(self.model.pyssizetclean)

        for i in range(self._imports_layout.count()):
            check_box = self._imports_layout.itemAt(i).widget()
            module_name = check_box.text()

            check_box.setEnabled(module_name != self.model.name)
            check_box.setChecked(module_name in self.model.imports)

    def get_fields(self):
        """ Update the API item from the dialog's fields. """

        self.model.outputdirsuffix = self._output_dir_suffix.text().strip()
        self.model.directives = self._directives.toPlainText().strip()
        self.model.callsuperinit = self._call_super_init.currentText().lower()
        self.model.virtualerrorhandler = self._virtual_error_handler.text().strip()
        self.model.pyssizetclean = self._py_ssizet_clean.isChecked()
        self.model.uselimitedapi = self._use_limited_api.isChecked()

        imports_list = []

        for i in range(self._imports_layout.count()):
            if self._imports_layout.itemAt(i).widget().isChecked():
                imports_list.append(self._all_imports[i])

        self.model.imports = imports_list

        return True
