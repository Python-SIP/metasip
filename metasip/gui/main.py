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

from PyQt6.QtWidgets import QApplication

from .api_editor import ApiEditor
from .project_ui import ProjectUi
from .shell import Shell
from .utils import warning

from ..dip.settings import SettingsManager
from ..dip.shell import IShell
from ..dip.shell.shells.main_window import MainWindowShell
from ..dip.shell.tools.dirty import DirtyTool
from ..dip.shell.tools.quit import QuitTool

from .. import UpdateManager
from ..project import Project
from ..updates import (ProjectV2Update, ProjectV3Update, ProjectV4Update,
        ProjectV5Update, ProjectV6Update, ProjectV7Update, ProjectV8Update,
        ProjectV9Update, ProjectV10Update, ProjectV11Update, ProjectV12Update,
        ProjectV13Update, ProjectV14Update, ProjectV15Update, ProjectV16Update)

from .tools import (FeaturesTool, ImportProjectTool, LoggerTool, ModulesTool,
        PlatformsTool, ScannerTool, VersionsTool)


def main():
    """ The entry point for the msip gui script. """

    # Parse the command line.
    parser = argparse.ArgumentParser()
    parser.add_argument('project', help="the project to edit", nargs='?')
    args = parser.parse_args()

    project_name = args.project

    app = QApplication(sys.argv)
    #SettingsManager.load('riverbankcomputing.com')

    # Add the project updates.
    #UpdateManager.updates.append(ProjectV2Update())
    #UpdateManager.updates.append(ProjectV3Update())
    #UpdateManager.updates.append(ProjectV4Update())
    #UpdateManager.updates.append(ProjectV5Update())
    #UpdateManager.updates.append(ProjectV6Update())
    #UpdateManager.updates.append(ProjectV7Update())
    #UpdateManager.updates.append(ProjectV8Update())
    #UpdateManager.updates.append(ProjectV9Update())
    #UpdateManager.updates.append(ProjectV10Update())
    #UpdateManager.updates.append(ProjectV11Update())
    #UpdateManager.updates.append(ProjectV12Update())
    #UpdateManager.updates.append(ProjectV13Update())
    #UpdateManager.updates.append(ProjectV14Update())
    #UpdateManager.updates.append(ProjectV15Update())
    #UpdateManager.updates.append(ProjectV16Update())

    # Define the shell.
    #shell_factory = MainWindowShell(main_area_policy='single',
    #        tool_factories=[LoggerTool, DirtyTool, QuitTool,
    #                lambda: editor_tool,
    #                FeaturesTool,
    #                ImportProjectTool,
    #                ModulesTool,
    #                PlatformsTool,
    #                ScannerTool,
    #                VersionsTool],
    #        title_template="[view][*]")

    # Create the shell.
    shell = Shell(ApiEditor(Project.factory(project_name, ui=ProjectUi())))

    # Handle any project passed on the command line.
    #if project_name is not None:
    #    try:
    #        IShell(shell).open('metasip.tools.project_editor', project_name,
    #                'metasip.formats.project')
    #    except StorageError as e:
    #        warning("Open", f"There was an error opening {project_name}.",
    #                detail=str(e))

    #SettingsManager.restore(shell.all_views())
    shell.show()
    rc = app.exec()
    #SettingsManager.save(shell.all_views())

    return rc
