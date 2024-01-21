# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


import os

from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QFileDialog

from ....models import Project
from ....project_io import load_project, save_project

from ...helpers import ProjectUi
from ...shell import EventType
from ...shell_tool import ShellTool, ShellToolLocation

from .api_editor import ApiEditor


class ApiEditorTool(ShellTool):
    """ This class implements the API editor tool. """

    def __init__(self, shell):
        """ Initialise the tool. """

        super().__init__(shell)

        self._api_editor = ApiEditor(shell)

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

        if event_type is EventType.API_STATUS:
            self._api_editor.api_status(event_arg)
        elif event_type is EventType.API_VERSIONS:
            self._api_editor.api_versions(event_arg)
        elif event_type is EventType.CONTAINER_API_ADD:
            self._api_editor.container_api_add(*event_arg)
        elif event_type is EventType.CONTAINER_API_DELETE:
            self._api_editor.container_api_delete(*event_arg)
        elif event_type is EventType.MODULE_ADD:
            self._api_editor.module_add(event_arg)
        elif event_type is EventType.MODULE_DELETE:
            self._api_editor.module_delete(event_arg)
        elif event_type is EventType.MODULE_RENAME:
            self._api_editor.module_rename(event_arg)
        elif event_type is EventType.PROJECT_NEW:
            self._api_editor.set_project()
        elif event_type is EventType.PROJECT_ROOT_MODULE_RENAME:
            self._api_editor.root_module_updated()

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

        saved = save_project(self.shell.project, ui=ProjectUi())
        if saved:
            self.shell.dirty = False

        return saved

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
            self.shell.project = Project()

    def _handle_open(self):
        """ Handle the Open action. """

        if self.shell.save_project():
            dir_name = os.path.dirname(self.shell.project.name)

            project_name, _ = QFileDialog.getOpenFileName(self._api_editor,
                    "Open project file", dir_name,
                    "MetaSIP project files (*.msp)")

            if project_name:
                project = Project(name=project_name)
                if load_project(project, ui=ProjectUi()):
                    self.shell.project = project

    def _handle_save(self):
        """ Handle the Save action. """

        if self.shell.project.name != '':
            self.save_data()
        else:
            self._handle_save_as()

    def _handle_save_as(self):
        """ Handle the Save as action. """

        dir_name = os.path.dirname(self.shell.project.name)

        project_name, _ = QFileDialog.getSaveFileName(self._api_editor,
                "Save project file", dir_name, "MetaSIP project files (*.msp)")

        if project_name:
            self.shell.project.name = project_name
            self.shell.notify(EventType.PROJECT_RENAME)
            self.save_data()
