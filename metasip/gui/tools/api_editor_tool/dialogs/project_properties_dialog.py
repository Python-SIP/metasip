# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QGridLayout, QLabel, QLineEdit, QPlainTextEdit

from ....helpers import BaseDialog
from ....shell import EventType


class ProjectPropertiesDialog(BaseDialog):
    """ This class implements the dialog for a project's properties. """

    def populate(self, layout):
        """ Populate the dialog's layout. """

        grid_layout = QGridLayout()
        layout.addLayout(grid_layout)

        grid_layout.addWidget(QLabel("Root package"), 0, 0)
        self._root_module = QLineEdit()
        grid_layout.addWidget(self._root_module, 0, 1, 1, 2)

        grid_layout.addWidget(QLabel("SIP file comments"), 1, 0,
                Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self._sip_comments = QPlainTextEdit()
        self._sip_comments.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        grid_layout.addWidget(self._sip_comments, 1, 1, 1, 2)

    def set_fields(self):
        """ Set the dialog's fields from the API item. """

        self._root_module.setText(self.model.rootmodule)
        self._sip_comments.setPlainText(self.model.sipcomments)

    def get_fields(self):
        """ Update the API item from the dialog's fields. """

        self.model.rootmodule = self._root_module.text().strip()
        self.model.sipcomments = self._sip_comments.toPlainText().strip()

        self.shell.notify(EventType.PROJECT_ROOT_MODULE_RENAME)

        return True
