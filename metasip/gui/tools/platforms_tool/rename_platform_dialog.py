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


from PyQt6.QtWidgets import QComboBox, QFormLayout, QLineEdit

from ...helpers import AbstractDialog

from ..helpers import tagged_items

from .helpers import init_platform_selector, validate_platform_name


class RenamePlatformDialog(AbstractDialog):
    """ This class implements the dialog for renaming a platform. """

    def populate(self, layout):
        """ Populate the dialog's layout. """

        self._platform = QComboBox()
        layout.addWidget(self._platform)

        form = QFormLayout()
        layout.addLayout(form)

        self._new_name = QLineEdit()
        form.addRow("New name", self._new_name)

    def set_fields(self):
        """ Set the dialog's fields from the project. """

        init_platform_selector(self._platform, self.model)

    def get_fields(self):
        """ Update the project from the dialog's fields. """

        project = self.model

        old_name = self._platform.currentText()

        new_name = self._new_name.text().strip()
        if not validate_platform_name(new_name, project, self):
            return False

        # Rename in each API item it appears.
        for api_item, _ in tagged_items(project):
            # Ignore items that aren't tagged with a platform.
            if len(api_item.platforms) == 0:
                continue

            # TODO - this should probably generate a lot more events.
            for i, p in enumerate(api_item.platforms):
                if p[0] == '!':
                    if p[1:] == old_name:
                        api_item.platforms[i] = '!' + new_name
                elif p == old_name:
                    api_item.platforms[i] = new_name

        # Rename in the project's list.
        project.platforms[project.platforms.index(old_name)] = new_name

        return True
