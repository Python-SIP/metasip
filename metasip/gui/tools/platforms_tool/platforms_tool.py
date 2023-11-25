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


class PlatformsTool(ActionTool):
    """ This class implements the platforms tool. """

    @property
    def actions(self):
        """ Get the destination menu and sequence of actions handled by the
        tool.
        """

        self._new_action = QAction("New Platform...",
                triggered=self._handle_new)
        self._rename_action = QAction("Rename Platform...",
                triggered=self._handle_rename)
        self._delete_action = QAction("Delete Platform...",
                triggered=self._handle_delete)

        return ("Edit",
                (self._new_action, self._rename_action, self._delete_action))

    def event(self, event_type):
        """ Reimplemented to handle project-specific events. """

        if event_type in (EventType.PROJECT_NEW, EventType.PLATFORM_ADD_DELETE):
            # Configure the actions.
            are_platforms = (len(self.shell.project.platforms) != 0)
            self._rename_action.setEnabled(are_platforms)
            self._delete_action.setEnabled(are_platforms)

    def _handle_delete(self):
        """ Handle the Delete action. """

        from .delete_platform_dialog import DeletePlatformDialog

        self.shell.handle_project_dialog("Delete Platform",
                DeletePlatformDialog, EventType.PLATFORM_ADD_DELETE)

    def _handle_new(self):
        """ Handle the New action. """

        from .new_platform_dialog import NewPlatformDialog

        self.shell.handle_project_dialog("New Platform", NewPlatformDialog,
                EventType.PLATFORM_ADD_DELETE)

    def _handle_rename(self):
        """ Handle the Rename action. """

        from .rename_platform_dialog import RenamePlatformDialog

        self.shell.handle_project_dialog("Rename Platform",
                RenamePlatformDialog)
