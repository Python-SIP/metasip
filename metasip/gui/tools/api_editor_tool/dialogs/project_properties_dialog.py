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


from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QComboBox, QGridLayout, QLabel, QLineEdit,
        QPlainTextEdit, QPushButton)

from ....helpers import BaseDialog


class ProjectPropertiesDialog(BaseDialog):
    """ This class implements the dialog for a project's properties. """

    def populate(self, layout):
        """ Populate the dialog's layout. """

        grid_layout = QGridLayout()
        layout.addLayout(grid_layout)

        grid_layout.addWidget(QLabel("Root package"), 0, 0)
        self._root_module = QLineEdit()
        grid_layout.addWidget(self._root_module, 0, 1, 1, 2)

        grid_layout.addWidget(QLabel("Ignored namespaces"), 1, 0)
        self._ignored_namespaces = QComboBox()
        grid_layout.addWidget(self._ignored_namespaces, 1, 1)
        self._remove_namespace = QPushButton("Remove namespace",
                clicked=self._handle_remove_namespace)
        grid_layout.addWidget(self._remove_namespace, 1, 2)

        grid_layout.addWidget(QLabel("SIP file comments"), 2, 0,
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self._sip_comments = QPlainTextEdit()
        self._sip_comments.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        grid_layout.addWidget(self._sip_comments, 2, 1, 1, 2)

    def set_fields(self):
        """ Set the dialog's fields from the API item. """

        self._root_module.setText(self.model.rootmodule)

        for namespace in self.model.ignorednamespaces:
            self._ignored_namespaces.addItem(namespace)

        self._enable_namespace_button()

        self._sip_comments.setPlainText(self.model.sipcomments)

    def get_fields(self):
        """ Update the API item from the dialog's fields. """

        self.model.rootmodule = self._root_module.text().strip()
        self.model.ignorednamespaces = [self._ignored_namespaces.itemText(i)
                for i in range(self._ignored_namespaces.count())]
        self.model.sipcomments = self._sip_comments.toPlainText().strip()

        return True

    def _handle_remove_namespace(self):
        """ Remove the current ignored namespace from the list. """

        idx = self._ignored_namespaces.currentIndex()

        if idx >= 0:
            self._ignored_namespaces.removeItem(idx)
            self._enable_namespace_button()

    def _enable_namespace_button(self):
        """ Enable or diable the button to remove the current namespace. """

        self._remove_namespace.setEnabled(self._ignored_namespaces.count())
