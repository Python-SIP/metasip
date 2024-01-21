# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


from PyQt6.QtWidgets import QComboBox

from ...helpers import BaseDialog

from ..helpers import tagged_items

from .helpers import delete_version, init_version_selector


class DeleteVersionDialog(BaseDialog):
    """ This class implements the dialog for deleting a version. """

    def populate(self, layout):
        """ Populate the dialog's layout. """

        self._version = QComboBox()
        layout.addWidget(self._version)

    def set_fields(self):
        """ Set the dialog's fields from the project. """

        init_version_selector(self._version, self.model)

    def get_fields(self):
        """ Update the project from the dialog's fields. """

        delete_version(self._version.currentText(), self.shell,
                migrate_items=True)

        return True
