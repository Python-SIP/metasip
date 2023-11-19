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

from ..project import AbstractProjectUi


class ProjectUi(AbstractProjectUi):
    """ This class encapsulates the UI-related methods supporting the loading
    of a project.
    """

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
