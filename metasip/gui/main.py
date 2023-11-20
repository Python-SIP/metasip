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

from ..dip.shell import IShell
from ..dip.shell.shells.main_window import MainWindowShell
from ..dip.shell.tools.quit import QuitTool

from .. import UpdateManager
from ..exceptions import UserException
from ..project import Project
from ..updates import (ProjectV2Update, ProjectV3Update, ProjectV4Update,
        ProjectV5Update, ProjectV6Update, ProjectV7Update, ProjectV8Update,
        ProjectV9Update, ProjectV10Update, ProjectV11Update, ProjectV12Update,
        ProjectV13Update, ProjectV14Update, ProjectV15Update, ProjectV16Update)

from .project_ui import ProjectUi
from .shell import Shell
from .tools import (ApiEditorTool, FeaturesTool, ImportProjectTool, LoggerTool,
        ModulesTool, PlatformsTool, ScannerTool, VersionsTool)
from .utils import warning


def main():
    """ The entry point for the msip gui script. """

    # Parse the command line.
    parser = argparse.ArgumentParser()
    parser.add_argument('project', help="the project to edit", nargs='?')
    args = parser.parse_args()

    project_name = args.project

    app = QApplication(sys.argv, applicationName='metasip',
            organizationDomain='riverbankcomputing.com',
            organizationName='Riverbank Computing')

    sys.excepthook = _exception_hook

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
    #        tool_factories=[LoggerTool, QuitTool,
    #                lambda: editor_tool,
    #                FeaturesTool,
    #                ImportProjectTool,
    #                ModulesTool,
    #                PlatformsTool,
    #                ScannerTool,
    #                VersionsTool],
    #        title_template="[view][*]")

    # Load any project.
    project = Project.factory(project_name, ui=ProjectUi())

    # Create the shell.
    shell = Shell(ApiEditorTool)

    # Set the project in the shell.
    shell.project = project

    # Launch the GUI.
    shell.show()
    return app.exec()


def _exception_hook(exc_type, exc_value, exc_tb):
    """ Handle an exception. """

    if isinstance(exc_value, UserException):
        from .utils import warning

        warning('metasip', exc_value.text, detail=exc_value.detail)
    else:
        import traceback

        tb = ''.join(traceback.format_exception(exc_type, exc_value, exc_tb))

        print(tb, file=sys.stderr)

        QApplication.exit(1)
