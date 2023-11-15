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

from ...dip.io import IFilterHints, IoManager
from ...dip.model import implements, Model
from ...dip.publish import ISubscriber
from ...dip.shell import IDirty, ITool
from ...dip.ui import (Action, Application, Dialog, IDialog,
        StorageLocationEditor)

from ...interfaces.project import IHeaderDirectory, IModule, IProject


@implements(ITool, ISubscriber)
class ImportProjectTool(Model):
    """ The ImportProjectTool implements a tool importing another project. """

    # The tool's dialog.
    dialog = Dialog(StorageLocationEditor('project_file', required=True),
            title="Import Project")

    # The tool's identifier.
    id = 'metasip.tools.import_project'

    # The action.
    import_action = Action(text="Import Project...",
            within='dip.ui.collections.tools')

    # The type of models we subscribe to.
    subscription_type = IProject

    @import_action.triggered
    def import_action(self):
        """ Invoked when the import action is triggered. """

        model = dict(project_file='')

        view = self.dialog(model)
        view.project_file.filter = IFilterHints(self.subscription.model).filter

        if IDialog(view).execute():
            # Create an empty project.
            project = type(self.subscription.model)()

            # Read the project to import.
            io_manager = IoManager().instance
            imported = io_manager.read(project, model['project_file'],
                    'metasip.formats.project')

            if imported is not None:
                try:
                    self._import_project(IProject(imported))
                except Exception as e:
                    Application.error("Import Project", str(e))

    def _import_project(self, imported):
        """ Import a project. """

        project = IProject(self.subscription.model)

        # Assume something will change.
        IDirty(project).dirty = True

        # Check the project being imported doesn't have any versions defined as
        # we don't support multiple timelines.
        if len(imported.versions) != 0:
            raise Exception(
                    "'{0}' defines one or more versions".format(
                            self._project_name(imported)))

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
                raise Exception(
                        "Both '{0}' and '{1}' define a '{2}' feature".format(
                                self._project_name(project),
                                self._project_name(imported), features))

        # Merge any externally defined modules.
        for module_name in list(project.externalmodules):
            for module in imported.modules:
                if IModule(module).name == module_name:
                    break
            else:
                project.externalmodules.remove(module_name)

        for module_name in imported.externalmodules:
            if module_name in project.externalmodules:
                continue

            for module in project.modules:
                if IModule(module).name == module_name:
                    break
            else:
                project.externalmodules.append(module_name)

        # Merge any platforms.
        for platform in imported.platforms:
            if platform not in project.platforms:
                project.platforms.append(platform)

        # Merge any ignored namespaces.
        for namespace in imported.ignorednamespaces:
            if namespace not in project.ignorednamespaces:
                project.ignorednamespaces.append(namespace)

        # Any any new modules and check for conflicts.
        for imported_module in imported.modules:
            for module in project.modules:
                if IModule(module).name == IModule(imported_module).name:
                    raise Exception(
                            "Both '{0}' and '{1}' define a '{2}' module".format(
                                    self._project_name(project),
                                    self._project_name(imported), features))

            project.modules.append(imported_module)

        # Any any new header directories and check for conflicts.
        for imported_headers in imported.headers:
            for headers in project.headers:
                if IHeaderDirectory(headers).name == IHeaderDirectory(imported_headers).name:
                    raise Exception(
                            "Both '{0}' and '{1}' define a '{2}' header directory".format(
                                    self._project_name(project),
                                    self._project_name(imported), features))

            project.headers.append(imported_headers)

    @staticmethod
    def _project_name(project):
        """ Return a project's name for use in user messages. """

        # TODO: the name should be an attribute of IProject and be implemented
        # as Project.__str__().
        return os.path.splitext(os.path.basename(project.name))[0]
