# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


from PyQt6.QtWidgets import QComboBox, QFormLayout

from .....models import VersionRange

from ....helpers import BaseDialog


class VersionsDialog(BaseDialog):
    """ This class implements the dialog for select the start and end versions.
    """

    def populate(self, layout):
        """ Populate the dialog's layout. """

        project = self.shell.project

        form = QFormLayout()
        layout.addLayout(form)

        start_combo_box = QComboBox()
        end_combo_box = QComboBox()

        # The start list will have the list of versions with the first version
        # replaced by "First".  The end list will have the list of versions
        # excluding the first version and with "Latest" appended.
        for i, version in enumerate(project.versions):
            if i == 0:
                # The first version never actually appears itself.
                start_combo_box.addItem("First", '')
            else:
                start_combo_box.addItem(version, version)
                end_combo_box.addItem(version, version)

        end_combo_box.addItem("Latest", '')

        form.addRow("Starting version", start_combo_box)
        form.addRow("Ending version", end_combo_box)

        self._start_combo_box = start_combo_box
        self._end_combo_box = end_combo_box

    def set_fields(self):
        """ Set the dialog's fields from the API item. """

        project = self.shell.project

        # Note that we ignore (and eventually discard) anything other than the
        # first version range.

        if len(self.model.versions) == 0:
            api_start = ''
            api_end = ''
        else:
            api_start = self.model.versions[0].startversion
            api_end = self.model.versions[0].endversion

        if api_start == '':
            start_index = 0
        else:
            start_index = project.versions.index(api_start)

        if api_end == '':
            end_index = len(project.versions) - 1
        else:
            end_index = project.versions.index(api_end) - 1

        self._start_combo_box.setCurrentIndex(start_index)
        self._end_combo_box.setCurrentIndex(end_index)

    def get_fields(self):
        """ Update the API item from the dialog's fields. """

        start_combo_box = self._start_combo_box
        end_combo_box = self._end_combo_box

        start_version = start_combo_box.itemData(start_combo_box.currentIndex())
        end_version = end_combo_box.itemData(end_combo_box.currentIndex())

        self.model.versions = [VersionRange(startversion=start_version, endversion=end_version)]

        return True
