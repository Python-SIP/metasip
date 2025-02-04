# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2025 Phil Thompson <phil@riverbankcomputing.com>


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
    if project_name:
        project = Project(project_name)
        if not load_project(project, ui=ProjectUi()):
            return 0
    else:
        project = Project('Untitled.msp')

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
