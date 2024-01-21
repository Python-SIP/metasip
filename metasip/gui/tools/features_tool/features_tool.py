# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


from PyQt6.QtGui import QAction

from ...shell import EventType
from ...shell_tool import ActionTool


class FeaturesTool(ActionTool):
    """ This class implements the features tool. """

    @property
    def actions(self):
        """ Get the destination menu and sequence of actions handled by the
        tool.
        """

        self._new_action = QAction("New Feature...",
                triggered=self._handle_new)
        self._rename_action = QAction("Rename Feature...",
                triggered=self._handle_rename)
        self._delete_action = QAction("Delete Feature...",
                triggered=self._handle_delete)

        return ("Edit",
                (self._new_action, self._rename_action, self._delete_action))

    def event(self, event_type, event_arg):
        """ Reimplemented to handle project-specific events. """

        if event_type in (EventType.PROJECT_NEW, EventType.FEATURE_ADD, EventType.FEATURE_DELETE):
            # Configure the actions.
            are_features = (len(self.shell.project.externalfeatures) + len(self.shell.project.features) != 0)
            self._rename_action.setEnabled(are_features)
            self._delete_action.setEnabled(are_features)

    @property
    def name(self):
        """ Get the tool's name. """

        return 'metasip.tool.features'

    def _handle_delete(self):
        """ Handle the Delete action. """

        from .delete_feature_dialog import DeleteFeatureDialog

        self.shell.handle_project_dialog("Delete Feature", DeleteFeatureDialog)

    def _handle_new(self):
        """ Handle the New action. """

        from .new_feature_dialog import NewFeatureDialog

        self.shell.handle_project_dialog("New Feature", NewFeatureDialog)

    def _handle_rename(self):
        """ Handle the Rename action. """

        from .rename_feature_dialog import RenameFeatureDialog

        self.shell.handle_project_dialog("Rename Feature", RenameFeatureDialog)
