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

        if project.version < (0, 17):
            self._output_dir_suffix = QLineEdit()
            form.addRow("Output directory suffix", self._output_dir_suffix)

        self._directives = QPlainTextEdit()
        self._directives.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        form.addRow("Additional directives", self._directives)

        self._call_super_init = QComboBox()
        self._call_super_init.addItems(("Undefined", "No", "Yes"))
        form.addRow("Call super().__init__()", self._call_super_init)

        self._keyword_arguments = QComboBox()
        self._keyword_arguments.addItems(("None", "All", "Optional"))
        form.addRow("Default handling of keyword arguments",
                self._keyword_arguments)

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

        module = self.model

        if self.shell.project.version < (0, 17):
            self._output_dir_suffix.setText(module.outputdirsuffix)

        self._directives.setPlainText(module.directives)

        if module.callsuperinit == 'undefined':
            idx = 0
        elif module.callsuperinit == 'no':
            idx = 1
        else:
            idx = 2

        self._call_super_init.setCurrentIndex(idx)

        if module.keywordarguments == 'Optional':
            idx = 2
        elif module.keywordarguments == 'All':
            idx = 1
        else:
            idx = 0

        self._keyword_arguments.setCurrentIndex(idx)

        self._virtual_error_handler.setText(module.virtualerrorhandler)
        self._use_limited_api.setChecked(module.uselimitedapi)
        self._py_ssizet_clean.setChecked(module.pyssizetclean)

        for i in range(self._imports_layout.count()):
            check_box = self._imports_layout.itemAt(i).widget()
            module_name = check_box.text()

            check_box.setEnabled(module_name != module.name)
            check_box.setChecked(module_name in module.imports)

    def get_fields(self):
        """ Update the API item from the dialog's fields. """

        module = self.model

        if self.shell.project.version < (0, 17):
            module.outputdirsuffix = self._output_dir_suffix.text().strip()

        module.directives = self._directives.toPlainText().strip()
        module.callsuperinit = self._call_super_init.currentText().lower()
        module.virtualerrorhandler = self._virtual_error_handler.text().strip()
        module.pyssizetclean = self._py_ssizet_clean.isChecked()
        module.uselimitedapi = self._use_limited_api.isChecked()

        module.keywordarguments = self._keyword_arguments.currentText()
        if module.keywordarguments == 'None':
            module.keywordarguments = ''

        imports_list = []

        for i in range(self._imports_layout.count()):
            if self._imports_layout.itemAt(i).widget().isChecked():
                imports_list.append(self._all_imports[i])

        module.imports = imports_list

        return True
