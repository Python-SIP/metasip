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
from enum import auto, Enum


class ToolLocation(Enum):
    """ The different possible locations for a tool in the shell. """

    CENTRE = auto()
    LEFT = auto()
    RIGHT = auto()
    TOP = auto()
    BOTTOM = auto()


class AbstractTool(ABC):
    """ An abstract base class for tools that handles common functionality. """

    def __init__(self, shell):
        """ Initialise the tool. """

        self.shell = shell
        self._project = None

    @property
    @abstractmethod
    def location(self):
        """ Get the location of the tool in the shell. """

        ...

    @property
    def project(self, project):
        """ Get the current project. """

        return self._project

    @project.setter
    def project(self, project):
        """ Set the current project. """

        self._project = project

    @property
    @abstractmethod
    def title(self):
        """ Get the tool's title. """

        ...

    @property
    @abstractmethod
    def widget(self):
        """ Get the tool's widget. """

        ...
