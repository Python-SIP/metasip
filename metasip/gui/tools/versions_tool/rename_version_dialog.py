# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


from PyQt6.QtWidgets import QComboBox, QFormLayout, QLineEdit

from ...helpers import BaseDialog
from ...shell import EventType

from ..helpers import tagged_items

from .helpers import init_version_selector, validate_version_name


class RenameVersionDialog(BaseDialog):
    """ This class implements the dialog for renaming a version. """

    def populate(self, layout):
        """ Populate the dialog's layout. """

        self._version = QComboBox()
        layout.addWidget(self._version)

        form = QFormLayout()
        layout.addLayout(form)

        self._new_name = QLineEdit()
        form.addRow("New name", self._new_name)

    def set_fields(self):
        """ Set the dialog's fields from the project. """

        init_version_selector(self._version, self.model)

    def get_fields(self):
        """ Update the project from the dialog's fields. """

        project = self.model

        old_name = self._version.currentText()

        new_name = self._new_name.text().strip()
        if not validate_version_name(new_name, project, self):
            return False

        # Rename in each API item it appears.
        for api_item, _ in tagged_items(project):
            for v in api_item.versions:
                if v.startversion == old_name:
                    v.startversion = new_name

                if v.endversion == old_name:
                    v.endversion = new_name

        # Rename in the header file versions.
        for hdir in project.headers:
            for hfile in hdir.content:
                for hfile_version in hfile.versions:
                    if hfile_version.version == old_name:
                        hfile_version.version = new_name

        # Rename in the project's list.
        project.versions[project.versions.index(old_name)] = new_name

        self.shell.notify(EventType.VERSION_RENAME, (old_name, new_name))

        return True
