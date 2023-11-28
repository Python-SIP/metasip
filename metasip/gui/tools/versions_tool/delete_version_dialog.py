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


from PyQt6.QtWidgets import QComboBox

from ...helpers import BaseDialog
from ...shell import EventType

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

        project = self.model

        version = self._version.currentText()

        # Delete from each API item it appears.
        delete_version(version, project, migrate_items=True)

        self.shell.notify(EventType.VERSION_ADD_DELETE)

        return True
