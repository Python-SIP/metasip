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

try:
    from PyQt6.QtWidgets import QApplication
except ImportError:
    print("Run \"pip install 'metasip[gui]'\" to install the additional GUI packages", file=sys.stderr)
    sys.exit(1)

from ..exceptions import UserException
from ..models import Project
from ..project_io import load_project

from .helpers import ProjectUi, warning
from .shell import Shell
from .tools import (ApiEditorTool, FeaturesTool, ImportProjectTool, LoggerTool,
        ModulesTool, PlatformsTool, ScannerTool, VersionsTool)


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

    # Load any project.
    project = Project(project_name)
    if not load_project(project, ui=ProjectUi()):
        return 0

    # Create the shell.
    shell = Shell(ApiEditorTool, FeaturesTool, ImportProjectTool, LoggerTool,
            ModulesTool, PlatformsTool, ScannerTool, VersionsTool)

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
