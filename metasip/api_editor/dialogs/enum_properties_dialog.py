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


from PyQt6.QtWidgets import (QCheckBox, QComboBox, QDialog, QFormLayout,
        QGroupBox, QLineEdit, QVBoxLayout)

from ..Annos import split_annos
from ..BaseType import BaseType

from .base_dialog import BaseDialog


class EnumPropertiesDialog(BaseDialog):
    """ This class implements the dialog for an enum's properties. """

    def populate(self):
        """ Populate the dialog's layout. """

        layout = self.layout()

        group_box = QGroupBox("Annotations")
        group_box_layout = QVBoxLayout()
        group_box.setLayout(group_box_layout)
        layout.addWidget(group_box)

        form = QFormLayout()
        group_box_layout.addLayout(form)

        py_name = QLineEdit()
        form.addRow("PyName", py_name)

        base_type = QComboBox()
        form.addRow("BaseType", base_type)
        base_type_helper = BaseType(base_type)

        no_scope = QCheckBox("NoScope")
        group_box_layout.addWidget(no_scope)

        no_type_hint = QCheckBox("NoTypeHint")
        group_box_layout.addWidget(no_type_hint)

        for name, value in split_annos(self.api_item.annos):
            if name == 'PyName':
                py_name.setText(value)
            elif name == 'BaseType':
                base_type_helper.setAnnotation(value)
            elif name == 'NoScope':
                no_scope.setChecked(True)
            elif name == 'NoTypeHint':
                no_type_hint.setChecked(True)

        self._py_name = py_name
        self._base_type_helper = base_type_helper
        self._no_scope = no_scope
        self._no_type_hint = no_type_hint

    def exec(self):
        """ Return the tuple of the enum's properties or None if the dialog was
        cancelled.
        """

        if super().exec() == int(QDialog.DialogCode.Rejected):
            return None

        annos_list = []

        self._base_type_helper.annotation(annos_list)

        s = self._py_name.text().strip()
        if s != '':
            annos_list.append('PyName=' + s)

        if self._no_scope.isChecked():
            annos_list.append('NoScope')

        if self._no_type_hint.isChecked():
            annos_list.append('NoTypeHint')

        return (','.join(annos_list), )
