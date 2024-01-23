# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


from PyQt6.QtWidgets import QApplication, QProgressDialog

from ...project_io import AbstractProjectUi

from .warning import warning


class ProjectUi(AbstractProjectUi):
    """ This class encapsulates the UI-related methods supporting the loading
    of a project.
    """

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

    def warn_minor_version_update(self, from_version, to_version):
        """ Called to warn the user that the project will be updated to the
        current minor version if saved.
        """

        from_s = f'{from_version[0]}.{from_version[1]}'
        to_s = f'{to_version[0]}.{to_version[1]}'

        warning("Update project format",
                f"The format of this project is v{from_s}. It will be automatically updated to v{to_s} if you save it.")
