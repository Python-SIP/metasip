# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


from abc import ABC, abstractmethod
from enum import auto, Enum


class ShellToolLocation(Enum):
    """ The different possible locations for a tool in the shell. """

    CENTRE = auto()
    LEFT = auto()
    RIGHT = auto()
    TOP = auto()
    BOTTOM = auto()


class ActionTool(ABC):
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

    @property
    @abstractmethod
    def name(self):
        """ Get the internal unique name of the tool. """

        ...

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


class ShellTool(ActionTool):
    """ A base class for tools that appear in a shell. """

    @property
    @abstractmethod
    def location(self):
        """ Get the location of the tool in the shell. """

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
