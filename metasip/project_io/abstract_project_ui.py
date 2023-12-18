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


from abc import ABC, abstractmethod


class AbstractProjectUi(ABC):
    """ This class encapsulates the UI-related methods supporting the loading
    of a project.
    """

    @abstractmethod
    def confirm_minor_version_update(self, from_version, to_version):
        """ Called to confirm with the user that the project can be updated
        from it's current minor version.  Return True if the user didn't
        cancel.
        """

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
