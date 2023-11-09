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


from PyQt6.QtWidgets import QComboBox, QDialog, QFormLayout

from .base_dialog import BaseDialog


class VersionsDialog(BaseDialog):
    """ This class implements the dialog for select the start and end versions.
    """

    def populate(self):
        """ Populate the dialog's layout. """

        layout = self.layout()

        form = QFormLayout()
        layout.addLayout(form)

        start_combo_box = QComboBox()
        end_combo_box = QComboBox()

        # The start list will have the list of versions with the first version
        # replaced by "First".  The end list will have the list of versions
        # excluding the first version and with "Latest" appended.
        for i, version in enumerate(self.project.versions):
            if i == 0:
                # The first version never actually appears itself.
                start_combo_box.addItem("First", '')
            else:
                start_combo_box.addItem(version, version)
                end_combo_box.addItem(version, version)

        end_combo_box.addItem("Latest", '')

        if len(self.api_item.versions) == 0:
            api_start = ''
            api_end = ''
        else:
            api_start = self.api_item.versions[0].startversion
            api_end = self.api_item.versions[0].endversion

        if api_start == '':
            start_index = 0
        else:
            start_index = self.project.versions.index(api_start)

        if api_end == '':
            end_index = len(self.project.versions) - 1
        else:
            end_index = self.project.versions.index(api_end) - 1

        start_combo_box.setCurrentIndex(start_index)
        end_combo_box.setCurrentIndex(end_index)

        form.addRow("Starting version", start_combo_box)
        form.addRow("Ending version", end_combo_box)

        self._start_combo_box = start_combo_box
        self._end_combo_box = end_combo_box

    def exec(self):
        """ Return a 2-tuple of the start and end versions or None if the
        dialog was cancelled.
        """

        if super().exec() == int(QDialog.DialogCode.Rejected):
            return None

        start_combo_box = self._start_combo_box
        end_combo_box = self._end_combo_box

        start_version = start_combo_box.itemData(start_combo_box.currentIndex())
        end_version = end_combo_box.itemData(end_combo_box.currentIndex())

        return (start_version, end_version)
