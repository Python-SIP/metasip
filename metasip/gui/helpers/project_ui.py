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


from PyQt6.QtWidgets import QApplication, QProgressDialog

from ...project_io import AbstractProjectUi

from .question import question
from .warning import warning


class ProjectUi(AbstractProjectUi):
    """ This class encapsulates the UI-related methods supporting the loading
    of a project.
    """

    def confirm_minor_version_update(self, from_version, to_version):
        """ Called to confirm with the user that the project can be updated
        from it's current minor version.  Return True if the user didn't
        cancel.
        """

        from_s = f'{from_version[0]}.{from_version[1]}'
        to_s = f'{to_version[0]}.{to_version[1]}'

        return question("Update project format",
                f"The project format is v{from_s}. Do you want to update it to {to_s}?")

    def error_creating_file(self, title, text, detail):
        """ Called when there was an error when creating a file. """

        warning(title, text, detail=detail)

    def load_starting(self, project, nr_steps):
        """ Called to initialise the UI prior to loading the project that will
        take a specific number of steps.
        """

        self._progress = QProgressDialog("Reading the project...", None, 0,
                nr_steps)
        self._progress.setWindowTitle(project.name)
        self._progress.setValue(0)

    def load_step(self):
        """ Called to update the UI once the next step of loading the project
        has been completed.
        """

        self._progress.setValue(self._progress.value() + 1)
        QApplication.processEvents()

    def update_project_format(self, root_element, from_version, to_version):
        """ Called to update the project from it's current major version before
        it is parsed.  Return True if the user didn't cancel.
        """

        # At the moment there is only one major version number.
        return True
