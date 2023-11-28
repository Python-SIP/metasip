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

        self.shell.notify(EventType.PLATFORM_ADD_DELETE)

        return True
