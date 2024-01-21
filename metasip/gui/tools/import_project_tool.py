# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


import os

from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QFileDialog

from ...models import Project
from ...project_io import load_project

from ..helpers import ProjectUi, warning
from ..shell_tool import ActionTool


class ImportProjectTool(ActionTool):
    """ This class implements a tool importing another project. """

    @property
    def actions(self):
        """ Get the destination menu and sequence of actions handled by the
        tool.
        """

        self._import_action = QAction("Import Project...",
                triggered=self._handle_import)

        return ("Tools", (self._import_action, ))

    @property
    def name(self):
        """ Get the tool's name. """

        return 'metasip.tool.import_project'

    def _handle_import(self):
        """ Handle the Import action. """

        dir_name = os.path.dirname(self.shell.project.name)

        import_name, _ = QFileDialog.getOpenFileName(self.shell.widget,
                "Import project file", dir_name,
                "MetaSIP project files (*.msp)")

        if import_name:
            imported = Project(name=import_name)
            if not load_project(imported, ui=ProjectUi()):
                return

            try:
                self._import_project(imported)
            except Exception as e:
                warning(str(e))

    def _import_project(self, imported):
        """ Import a project. """

        project = self.shell.project

        project_name = self._project_name(project)
        imported_name = self._project_name(imported)

        # Check the project being imported doesn't have any versions defined as
        # we don't support multiple timelines.
        if len(imported.versions) != 0:
            raise Exception(f"'{imported_name}' defines one or more versions")

        # Merge any external features.
        for feature in list(project.externalfeatures):
            if feature in imported.features:
                project.externalfeatures.remove(feature)

        for feature in imported.externalfeatures:
            if feature in project.features:
                continue

            if feature in project.externalfeatures:
                continue

            project.externalfeatures.append(feature)

        # Add any new features and check for conflicts.
        for feature in imported.features:
            if feature in project.features:
                raise Exception(f"Both '{project_name}' and '{imported_name}' define a '{feature}' feature")

        # Merge any externally defined modules.
        for module_name in list(project.externalmodules):
            for module in imported.modules:
                if module.name == module_name:
                    break
            else:
                project.externalmodules.remove(module_name)

        for module_name in imported.externalmodules:
            if module_name in project.externalmodules:
                continue

            for module in project.modules:
                if module.name == module_name:
                    break
            else:
                project.externalmodules.append(module_name)

        # Merge any platforms.
        for platform in imported.platforms:
            if platform not in project.platforms:
                project.platforms.append(platform)

        # Any any new modules and check for conflicts.
        for imported_module in imported.modules:
            for module in project.modules:
                if module.name == imported_module.name:
                    raise Exception(f"Both '{project_name}' and '{imported_name}' define a '{module.name}' module")

            project.modules.append(imported_module)

        # Any any new header directories and check for conflicts.
        for imported_header in imported.headers:
            for header in project.headers:
                if header.name == imported_header.name:
                    raise Exception(f"Both '{project_name}' and '{imported_name}' define a '{header.name}' header directory")

            project.headers.append(imported_headers)

        self.shell.dirty = True

    @staticmethod
    def _project_name(project):
        """ Return a project's name for use in user messages. """

        return os.path.splitext(os.path.basename(project.name))[0]
