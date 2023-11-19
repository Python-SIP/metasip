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


from PyQt6.QtWidgets import QCheckBox, QDialog

from .abstract_dialog import AbstractDialog


class PlatformsDialog(AbstractDialog):
    """ This class implements the dialog for selecting a number of platforms.
    """

    def populate(self, layout):
        """ Populate the dialog's layout. """

        self._platforms = []

        for platform in self.project.platforms:
            check_box = QCheckBox(platform)
            layout.addWidget(check_box)
            self._platforms.append((check_box, platform))

    def set_fields(self):
        """ Set the dialog's fields from the API item. """

        for check_box, platform in self._platforms:
            check_box.setChecked(platform in self.api_item.platforms)

    def get_fields(self):
        """ Update the API item from the dialog's fields. """

        platforms = []

        for check_box, platform in self._platforms:
            if check_box.isChecked():
                platforms.append(platform)

        self.api_item.platforms = platforms
