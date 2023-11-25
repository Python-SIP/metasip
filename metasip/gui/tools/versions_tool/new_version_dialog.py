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

from .helpers import init_version_selector, validate_version_name


class NewVersionDialog(AbstractDialog):
    """ This class implements the dialog for creating a new version. """

    def populate(self, layout):
        """ Populate the dialog's layout. """

        form = QFormLayout()
        layout.addLayout(form)

        self._version = QLineEdit()
        form.addRow("Version name", self._version)

        self._after = QComboBox()
        form.addRow("Add version after", self._after)

    def set_fields(self):
        """ Set the dialog's fields from the project. """

        project = self.model

        init_version_selector(self._after, self.model)

        if len(project.versions) != 0:
            self._after.setEnabled(True)
            self._after.setCurrentText(project.versions[-1])
        else:
            self._after.setEnabled(False)

    def get_fields(self):
        """ Update the project from the dialog's fields. """

        project = self.model

        version = self._version.text().strip()
        if not validate_version_name(version, project, self):
            return False

        # Add to the header file versions.
        # TODO - this probably needs to generate events.
        if self._after.isEnabled():
            after = self._after.currentText()

            # Create a new header file version based on the previous one.
            for hdir in project.headers:
                scan = False

                for hfile in hdir.content:
                    for hfile_version in hfile.versions:
                        if hfile_version == after:
                            new_hfile_version = HeaderFileVersion(
                                    md5=hfile_version.md5, parse=False,
                                    version=version)
                            hfile.versions.append(new_hfile_version)

                            # The header directory needs scanning.
                            scan = True

                            break

                if scan:
                    hdir.scan.append(version)

            project.versions.insert(project.versions.index(after) + 1, version)
        else:
            # The first explicit version has been defined.
            for hdir in project.headers:
                for hfile in hdir.content:
                    # There will only be one version at most defined.
                    if len(hfile.versions) != 0:
                        hfile.versions[0].version = version

            project.versions.append(version)

        return True
