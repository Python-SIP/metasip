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

        if event_type in (EventType.PROJECT_NEW, EventType.MODULE_ADD_DELETE):
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

        self.shell.handle_project_dialog("Delete Module", DeleteModuleDialog,
                EventType.MODULE_ADD_DELETE)

    def _handle_new(self):
        """ Handle the New action. """

        from .new_module_dialog import NewModuleDialog

        self.shell.handle_project_dialog("New Module", NewModuleDialog,
                EventType.MODULE_ADD_DELETE)

    def _handle_rename(self):
        """ Handle the Rename action. """

        from .rename_module_dialog import RenameModuleDialog

        self.shell.handle_project_dialog("Rename Module", RenameModuleDialog)
