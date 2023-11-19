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


from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDockWidget, QMainWindow

from .tools import ToolLocation


class Shell:
    """ This class encapsulates a collection of tools. """

    # Map tool locations to Qt dock areas.
    _LOCATION_MAP = {
        ToolLocation.LEFT: Qt.DockWidgetArea.LeftDockWidgetArea,
        ToolLocation.RIGHT: Qt.DockWidgetArea.RightDockWidgetArea,
        ToolLocation.TOP: Qt.DockWidgetArea.TopDockWidgetArea,
        ToolLocation.BOTTOM: Qt.DockWidgetArea.BottomDockWidgetArea,
    }

    def __init__(self, *tool_factories):
        """ Initialise the shell. """

        self._project = None

        # Create the widget that implements the shell.
        self._shell_widget = QMainWindow()

        # Create the tools.
        self._tools = []

        for tool_factory in tool_factories:
            tool = tool_factory(self)

            if tool.location is ToolLocation.CENTRE:
                self._shell_widget.setCentralWidget(tool.widget)
            else:
                self._shell_widget.addDockWidget(
                        self._LOCATION_MAP[tool.location],
                        QDockWidget(tool.title, tool.widget))

            self._tools.append(tool)

    @property
    def dirty(self):
        """ Get the project's dirty state. """

        return self._project.dirty

    @dirty.setter
    def dirty(self, state):
        """ Set the dirty state. """

        self._project.dirty = state
        self._shell_widget.setWindowModified(state)

    @property
    def project(self):
        """ Get the current project. """

        return self._project

    @project.setter
    def project(self, project):
        """ Set the current project. """

        self._project = project

        for tool in self._tools:
            tool.project = project

        self._shell_widget.setWindowTitle(project.name + '[*]')

        self.dirty = False

    def show(self):
        """ Make the shell visible. """

        self._shell_widget.show()

