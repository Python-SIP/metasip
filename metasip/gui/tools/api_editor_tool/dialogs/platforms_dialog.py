# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


from PyQt6.QtWidgets import QCheckBox, QDialog

from ....helpers import BaseDialog


class PlatformsDialog(BaseDialog):
    """ This class implements the dialog for selecting a number of platforms.
    """

    def populate(self, layout):
        """ Populate the dialog's layout. """

        project = self.shell.project

        self._platforms = []

        for platform in project.platforms:
            check_box = QCheckBox(platform)
            layout.addWidget(check_box)
            self._platforms.append((check_box, platform))

    def set_fields(self):
        """ Set the dialog's fields from the API item. """

        for check_box, platform in self._platforms:
            check_box.setChecked(platform in self.model.platforms)

    def get_fields(self):
        """ Update the API item from the dialog's fields. """

        platforms = []

        for check_box, platform in self._platforms:
            if check_box.isChecked():
                platforms.append(platform)

        self.model.platforms = platforms

        return True
