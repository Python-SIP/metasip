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


import os

from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QFileDialog

from ....project import Project

from ...helpers import ProjectUi
from ...shell import EventType
from ...shell_tool import ShellTool, ShellToolLocation

from .api_editor import ApiEditor


class ApiEditorTool(ShellTool):
    """ This class implements the API editor tool. """

    def __init__(self, shell):
        """ Initialise the tool. """

        super().__init__(shell)

        self._api_editor = ApiEditor(self)

    @property
    def actions(self):
        """ Get the destination menu and sequence of actions handled by the
        tool.
        """

        new_action = QAction("New", self._api_editor,
                triggered=self._handle_new)
        open_action = QAction("Open...", self._api_editor,
                triggered=self._handle_open)
        save_action = QAction("Save", self._api_editor,
                triggered=self._handle_save)
        save_as_action = QAction("Save as...", self._api_editor,
                triggered=self._handle_save_as)

        return "File", (new_action, open_action, save_action, save_as_action)

    def event(self, event_type, event_arg):
        """ Reimplemented to handle project-specific events. """

        if event_type is EventType.PROJECT_NEW:
            self._api_editor.set_project(self.shell.project)

    @property
    def location(self):
        """ Get the location of the tool in the shell. """

        return ShellToolLocation.CENTRE

    @property
    def name(self):
        """ Get the tool's name. """

        return 'metasip.tool.api_editor'

    def restore_state(self, settings):
        """ Restore the tool's state from the settings. """

        self._api_editor.restore_state(settings)

    def save_data(self):
        """ Save the tool's data and return True if there was no error. """

        return self.shell.project.save()

    def save_state(self, settings):
        """ Save the tool's state in the settings. """

        self._api_editor.save_state(settings)

    @property
    def title(self):
        """ Get the tool's title. """

        return "API Editor"

    @property
    def widget(self):
        """ Get the tool's widget. """

        return self._api_editor

    def _handle_new(self):
        """ Handle the New action. """

        if self.shell.save_project():
            self.shell.project = Project.factory()

    def _handle_open(self):
        """ Handle the Open action. """

        if self.shell.save_project():
            dir_name = os.path.dirname(self.shell.project.name)

            project_name, _ = QFileDialog.getOpenFileName(self._api_editor,
                    "Open project file", dir_name,
                    "MetaSIP project files (*.msp)")

            if project_name:
                self.shell.project = Project.factory(project_name=project_name,
                        ui=ProjectUi())

    def _handle_save(self):
        """ Handle the Save action. """

        self.save_data()

    def _handle_save_as(self):
        """ Handle the Save as action. """

        dir_name = os.path.dirname(self.shell.project.name)

        project_name, _ = QFileDialog.getSaveFileName(self._api_editor,
                "Save project file", dir_name, "MetaSIP project files (*.msp)")

        if project_name:
            self.shell.project.project_name = project_name
            self.shell.project_name = project_name
            self.shell.project.save(project_name)
            self.shell.dirty = False
