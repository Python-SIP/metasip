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


from PyQt6.QtWidgets import (QCheckBox, QComboBox, QFormLayout, QGridLayout,
        QGroupBox, QLineEdit, QPlainTextEdit)

from .abstract_dialog import AbstractDialog


class ModulePropertiesDialog(AbstractDialog):
    """ This class implements the dialog for a module's properties. """

    def populate(self, layout):
        """ Populate the dialog's layout. """

        self._all_imports = list(self.project.externalmodules)
        self._all_imports.extend([m.name for m in self.project.modules])
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

        self._output_dir_suffix.setText(self.api_item.outputdirsuffix)
        self._directives.setPlainText(self.api_item.directives)

        if self.api_item.callsuperinit == 'undefined':
            idx = 0
        elif self.api_item.callsuperinit == 'no':
            idx = 1
        else:
            idx = 2

        self._call_super_init.setCurrentIndex(idx)

        self._virtual_error_handler.setText(self.api_item.virtualerrorhandler)
        self._use_limited_api.setChecked(self.api_item.uselimitedapi)
        self._py_ssizet_clean.setChecked(self.api_item.pyssizetclean)

        for i in range(self._imports_layout.count()):
            check_box = self._imports_layout.itemAt(i).widget()
            module_name = check_box.text()

            check_box.setEnabled(module_name != self.api_item.name)
            check_box.setChecked(module_name in self.api_item.imports)

    def get_fields(self):
        """ Update the API item from the dialog's fields. """

        self.api_item.outputdirsuffix = self._output_dir_suffix.text().strip()
        self.api_item.directives = self._directives.toPlainText().strip()
        self.api_item.callsuperinit = self._call_super_init.currentText().lower()
        self.api_item.virtualerrorhandler = self._virtual_error_handler.text().strip()
        self.api_item.pyssizetclean = self._py_ssizet_clean.isChecked()
        self.api_item.uselimitedapi = self._use_limited_api.isChecked()

        imports_list = []

        for i in range(self._imports_layout.count()):
            if self._imports_layout.itemAt(i).widget().isChecked():
                imports_list.append(self._all_imports[i])

        self.api_item.imports = imports_list
