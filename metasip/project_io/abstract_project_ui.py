# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


from abc import ABC, abstractmethod


class AbstractProjectUi(ABC):
    """ This class encapsulates the UI-related methods supporting the loading
    of a project.
    """

    @abstractmethod
    def error_creating_file(self, title, text, detail):
        """ Called when there was an error when creating a file. """

        ...

    @abstractmethod
    def load_starting(self, project, nr_steps):
        """ Called to initialise the UI prior to loading the project that will
        take a specific number of steps.
        """

        ...

    @abstractmethod
    def load_step(self):
        """ Called to update the UI once the next step of loading the project
        has been completed.
        """

        ...

    @abstractmethod
    def update_project_format(self, root_element, from_version, to_version):
        """ Called to update the project from it's current major version before
        it is parsed.  Return True if the user didn't cancel.
        """

        ...

    @abstractmethod
    def warn_minor_version_update(self, from_version, to_version):
        """ Called to warn the user that the project will be updated to the
        current minor version if saved.
        """

        ...
