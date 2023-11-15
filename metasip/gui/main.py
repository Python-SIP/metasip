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


import argparse
import sys

from ..dip.io import IoManager, StorageError
from ..dip.io.storage.filesystem import FilesystemStorageFactory
from ..dip.settings import SettingsManager
from ..dip.shell import IShell
from ..dip.shell.shells.main_window import MainWindowShell
from ..dip.shell.tools.dirty import DirtyTool
from ..dip.shell.tools.model_manager import ModelManagerTool
from ..dip.shell.tools.quit import QuitTool
from ..dip.ui import Application

from .. import Project, ProjectCodec, ProjectFactory, UpdateManager
from ..updates import (ProjectV2Update, ProjectV3Update, ProjectV4Update,
        ProjectV5Update, ProjectV6Update, ProjectV7Update, ProjectV8Update,
        ProjectV9Update, ProjectV10Update, ProjectV11Update, ProjectV12Update,
        ProjectV13Update, ProjectV14Update, ProjectV15Update, ProjectV16Update)

from .tools.features_tool import FeaturesTool
from .tools.import_project_tool import ImportProjectTool
from .tools.logger_tool import LoggerTool
from .tools.modules_tool import ModulesTool
from .tools.platforms_tool import PlatformsTool
from .tools.scanner_tool import ScannerTool
from .tools.versions_tool import VersionsTool

from .project_editor_tool import ProjectEditorTool


def main():
    """ The entry point for the msip gui script. """

    # Parse the command line.
    parser = argparse.ArgumentParser()
    parser.add_argument('project', help="the project to edit", nargs='?')
    args = parser.parse_args()

    return _launch_gui(args.project, sys.argv)


def _launch_gui(project_name, gui_args):
    """ Launch the GUI for a project. """

    # Configure the i/o manager for reading and writing projects to the
    # filesystem.
    IoManager.codecs.append(ProjectCodec())
    IoManager.storage_factories.append(FilesystemStorageFactory())

    app = Application(gui_args)
    SettingsManager.load('riverbankcomputing.com')

    # Add the project updates.
    UpdateManager.updates.append(ProjectV2Update())
    UpdateManager.updates.append(ProjectV3Update())
    UpdateManager.updates.append(ProjectV4Update())
    UpdateManager.updates.append(ProjectV5Update())
    UpdateManager.updates.append(ProjectV6Update())
    UpdateManager.updates.append(ProjectV7Update())
    UpdateManager.updates.append(ProjectV8Update())
    UpdateManager.updates.append(ProjectV9Update())
    UpdateManager.updates.append(ProjectV10Update())
    UpdateManager.updates.append(ProjectV11Update())
    UpdateManager.updates.append(ProjectV12Update())
    UpdateManager.updates.append(ProjectV13Update())
    UpdateManager.updates.append(ProjectV14Update())
    UpdateManager.updates.append(ProjectV15Update())
    UpdateManager.updates.append(ProjectV16Update())

    # Define the shell.
    editor_tool = ProjectEditorTool(model_policy='one')

    view_factory = MainWindowShell(main_area_policy='single',
            tool_factories=[LoggerTool, DirtyTool, QuitTool,
                    lambda: ModelManagerTool(
                            model_factories=[ProjectFactory()]),
                    lambda: editor_tool,
                    FeaturesTool,
                    ImportProjectTool,
                    ModulesTool,
                    PlatformsTool,
                    ScannerTool,
                    VersionsTool],
            title_template="[view][*]")

    # Create the shell.
    view = view_factory()

    # Handle any project passed on the command line.
    if project_name is not None:
        try:
            IShell(view).open('metasip.tools.project_editor', project_name,
                    'metasip.formats.project')
        except StorageError as e:
            Application.warning("Open",
                    f"There was an error opening {project_name}.",
                    detail=str(e))

    SettingsManager.restore(view.all_views())
    view.visible = True
    rc = app.execute()
    SettingsManager.save(view.all_views())

    return rc
