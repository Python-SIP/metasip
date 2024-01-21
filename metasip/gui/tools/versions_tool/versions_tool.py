# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


from PyQt6.QtGui import QAction

from ...helpers import question
from ...shell import EventType
from ...shell_tool import ActionTool

from .helpers import delete_version


class VersionsTool(ActionTool):
    """ This class implements the versions tool. """

    @property
    def actions(self):
        """ Get the destination menu and sequence of actions handled by the
        tool.
        """

        self._new_action = QAction("New Version...",
                triggered=self._handle_new)
        self._rename_action = QAction("Rename Version...",
                triggered=self._handle_rename)
        self._delete_action = QAction("Delete Version...",
                triggered=self._handle_delete)
        self._delete_all_action = QAction("Delete All Versions...",
                triggered=self._handle_delete_all)

        return ("Edit",
                (self._new_action, self._rename_action, self._delete_action,
                        self._delete_all_action))

    def event(self, event_type, event_arg):
        """ Reimplemented to handle project-specific events. """

        if event_type in (EventType.PROJECT_NEW, EventType.VERSION_ADD, EventType.VERSION_DELETE):
            # Configure the actions.
            are_versions = (len(self.shell.project.versions) != 0)
            self._rename_action.setEnabled(are_versions)
            self._delete_action.setEnabled(are_versions)
            self._delete_all_action.setEnabled(are_versions)

    @property
    def name(self):
        """ Get the tool's name. """

        return 'metasip.tool.versions'

    def _handle_delete(self):
        """ Handle the Delete action. """

        from .delete_version_dialog import DeleteVersionDialog

        self.shell.handle_project_dialog("Delete Version", DeleteVersionDialog)

    def _handle_delete_all(self):
        """ Handle the Delete All action. """

        confirmed = question("Delete All Versions",
                "All versions will be removed along with any API items that "
                "are not part of the latest version.\n\nDo you wish to "
                "continue?",
                parent=self.shell.widget)

        if confirmed:
            for version in list(self.shell.project.versions):
                delete_version(version, self.shell, migrate_items=False)

            self.shell.dirty = True

    def _handle_new(self):
        """ Handle the New action. """

        from .new_version_dialog import NewVersionDialog

        self.shell.handle_project_dialog("New Version", NewVersionDialog)

    def _handle_rename(self):
        """ Handle the Rename action. """

        from .rename_version_dialog import RenameVersionDialog

        self.shell.handle_project_dialog("Rename Version", RenameVersionDialog)
