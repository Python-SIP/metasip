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


from abc import ABCMeta, abstractmethod
from enum import auto, Enum


class ShellToolLocation(Enum):
    """ The different possible locations for a tool in the shell. """

    CENTRE = auto()
    LEFT = auto()
    RIGHT = auto()
    TOP = auto()
    BOTTOM = auto()


class ActionTool:
    """ A base class for tools that implement optional actions. """

    def __init__(self, shell):
        """ Initialise the tool. """

        self.shell = shell

    @property
    def actions(self):
        """ Get the destination menu and sequence of actions handled by the
        tool.
        """

        # This default implementation does nothing.
        return None, ()

    def event(self, event_type, event_arg):
        """ This is called whenever a project-specific event takes place. """

        # This default implementation does nothing.
        pass

    def restore_state(self, settings):
        """ Restore the tool's state from the settings. """

        # This default implementation does nothing.
        pass

    def save_data(self):
        """ Save the tool's data and return True if there was no error. """

        # This default implementation does nothing.
        return True

    def save_state(self, settings):
        """ Save the tool's state in the settings. """

        # This default implementation does nothing.
        pass


class ShellTool(ActionTool, metaclass=ABCMeta):
    """ A base class for tools that appear in a shell. """

    @property
    @abstractmethod
    def location(self):
        """ Get the location of the tool in the shell. """

        ...

    @property
    @abstractmethod
    def name(self):
        """ Get the internal unique name of the tool. """

        ...

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
