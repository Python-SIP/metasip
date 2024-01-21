# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


from PyQt6.QtWidgets import QFormLayout, QLineEdit

from ...helpers import BaseDialog
from ...shell import EventType

from .helpers import validate_platform_name


class NewPlatformDialog(BaseDialog):
    """ This class implements the dialog for creating a new platform. """

    def populate(self, layout):
        """ Populate the dialog's layout. """

        form = QFormLayout()
        layout.addLayout(form)

        self._platform = QLineEdit()
        form.addRow("Platform name", self._platform)

    def get_fields(self):
        """ Update the project from the dialog's fields. """

        project = self.model

        platform = self._platform.text().strip()
        if not validate_platform_name(platform, project, self):
            return False

        project.platforms.append(platform)

        self.shell.notify(EventType.PLATFORM_ADD, platform)

        return True
