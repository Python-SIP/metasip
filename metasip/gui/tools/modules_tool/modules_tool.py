# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


from PyQt6.QtGui import QAction

from ...shell import EventType
from ...shell_tool import ActionTool


class ModulesTool(ActionTool):
    """ This class implements the modules tool. """

    @property
    def actions(self):
        """ Get the destination menu and sequence of actions handled by the
        tool.
        """

        self._new_action = QAction("New Module...",
                triggered=self._handle_new)
        self._rename_action = QAction("Rename Module...",
                triggered=self._handle_rename)
        self._delete_action = QAction("Delete Module...",
                triggered=self._handle_delete)

        return ("Edit",
                (self._new_action, self._rename_action, self._delete_action))

    def event(self, event_type, event_arg):
        """ Reimplemented to handle project-specific events. """

        if event_type in (EventType.PROJECT_NEW, EventType.MODULE_ADD, EventType.MODULE_DELETE):
            # Configure the actions.
            are_modules = (len(self.shell.project.modules) != 0)
            self._rename_action.setEnabled(are_modules)
            self._delete_action.setEnabled(are_modules)

    @property
    def name(self):
        """ Get the tool's name. """

        return 'metasip.tool.modules'

    def _handle_delete(self):
        """ Handle the Delete action. """

        from .delete_module_dialog import DeleteModuleDialog

        self.shell.handle_project_dialog("Delete Module", DeleteModuleDialog)

    def _handle_new(self):
        """ Handle the New action. """

        from .new_module_dialog import NewModuleDialog

        self.shell.handle_project_dialog("New Module", NewModuleDialog)

    def _handle_rename(self):
        """ Handle the Rename action. """

        from .rename_module_dialog import RenameModuleDialog

        self.shell.handle_project_dialog("Rename Module", RenameModuleDialog)
