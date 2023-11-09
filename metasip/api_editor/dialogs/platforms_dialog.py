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

from .base_dialog import BaseDialog


class PlatformsDialog(BaseDialog):
    """ This class implements the dialog for selecting a number of platforms.
    """

    def populate(self):
        """ Populate the dialog's layout. """

        layout = self.layout()

        for platform_nr, platform in enumerate(self.project.platforms):
            check_box = QCheckBox(platform)

            if platform in self.api_item.platforms:
                check_box.setChecked(True)

            layout.insertWidget(platform_nr, check_box)

    def exec(self):
        """ Return the list of platforms or None if the dialog was cancelled.
        """

        if super().exec() == int(QDialog.DialogCode.Rejected):
            return None

        layout = self.layout()

        platforms = []

        for platform_nr in range(layout.count()):
            check_box = layout.itemAt(platform_nr).widget()

            if isinstance(check_box, QCheckBox) and check_box.isChecked():
                platforms.append(self.project.platforms[platform_nr])

        return platforms
