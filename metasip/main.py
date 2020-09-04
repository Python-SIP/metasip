# Copyright (c) 2020 Riverbank Computing Limited.
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
import os

from dip.io import IoManager, StorageError
from dip.io.storage.filesystem import FilesystemStorageFactory

from . import Project, ProjectCodec


# Configure the i/o manager so we can use it for reading and writing projects
# to the filesystem.
IoManager.codecs.append(ProjectCodec())
IoManager.storage_factories.append(FilesystemStorageFactory())


def load_batch_project(prjname):
    """ Load an existing project in anticipation of doing some batch
    processing.

    :param prjname:
        is the location of the project.
    :return:
        the project.
    """

    if not prjname:
        fatal("Specify the name of an existing project file")

    try:
        prj = IoManager.read(Project(), prjname, 'metasip.formats.project')
    except StorageError as e:
        fatal(e.error)

    return prj


def generate(prjname, gendir, latest_sip):
    """
    Generate the .sip files for a project and return an exit code or 0 if there
    was no error.

    prjname is the name of the project file.
    gendir is the directory in which to generate the .sip files.
    """
    if not os.path.isdir(gendir):
        fatal("%s is not an existing directory" % gendir)

    prj = load_batch_project(prjname)

    # Generate each module.
    for mod in prj.modules:
        if not prj.generateModule(mod, gendir, latest_sip=latest_sip):
            fatal(prj.diagnostic)

    # No error if we have got this far.
    return 0


def launchGUI(prjname, guiargs):
    """ Launch the GUI for a project.

    :param prjname:
        is the name of the project file.  It is None if there is none.
    :param guiargs:
        is a sequence of additional toolkit-specific arguments.
    :return:
        the exit code or 0 if there was no error.
    """

    from dip.io import StorageError
    from dip.settings import SettingsManager
    from dip.shell import IShell
    from dip.shell.shells.main_window import MainWindowShell
    from dip.shell.tools.dirty import DirtyTool
    from dip.shell.tools.model_manager import ModelManagerTool
    from dip.shell.tools.quit import QuitTool
    from dip.ui import Application

    from metasip import ProjectEditorTool, ProjectFactory, UpdateManager
    from metasip.schemas import (ProjectV1Schema, ProjectV2Schema,
            ProjectV3Schema, ProjectV4Schema, ProjectV5Schema, ProjectV6Schema,
            ProjectV7Schema, ProjectV8Schema, ProjectV9Schema,
            ProjectV10Schema, ProjectV11Schema, ProjectV12Schema,
            ProjectV13Schema, ProjectV14Schema)
    from metasip.tools.features import FeaturesTool
    from metasip.tools.logger import LoggerTool
    from metasip.tools.modules import ModulesTool
    from metasip.tools.platforms import PlatformsTool
    from metasip.tools.scanner import ScannerTool
    from metasip.tools.schema_validator import SchemaValidatorTool
    from metasip.tools.versions import VersionsTool
    from metasip.updates import (ProjectV2Update, ProjectV3Update,
            ProjectV4Update, ProjectV5Update, ProjectV6Update, ProjectV7Update,
            ProjectV8Update, ProjectV9Update, ProjectV10Update,
            ProjectV11Update, ProjectV12Update, ProjectV13Update,
            ProjectV14Update)

    app = Application(guiargs)
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

    # Define the shell.
    editor_tool = ProjectEditorTool(model_policy='one')

    view_factory = MainWindowShell(main_area_policy='single',
            tool_factories=[LoggerTool, DirtyTool, QuitTool,
                    lambda: ModelManagerTool(
                            model_factories=[ProjectFactory()]),
                    lambda: editor_tool,
                    FeaturesTool,
                    ModuleAutofillTool,
                    ModulesTool,
                    PlatformsTool,
                    ScannerTool,
                    lambda: SchemaValidatorTool(
                            schemas=[ProjectV1Schema(), ProjectV2Schema(),
                                    ProjectV3Schema(), ProjectV4Schema(),
                                    ProjectV5Schema(), ProjectV6Schema(),
                                    ProjectV7Schema(), ProjectV8Schema(),
                                    ProjectV9Schema(), ProjectV10Schema(),
                                    ProjectV11Schema(), ProjectV12Schema(),
                                    ProjectV13Schema(), ProjectV14Schema()]),
                    VersionsTool],
            title_template="[view][*]")

    # Create the shell.
    view = view_factory()

    # Handle any project passed on the command line.
    if prjname is not None:
        try:
            IShell(view).open('metasip.tools.project_editor', prjname,
                    'metasip.formats.project')
        except StorageError as e:
            Application.warning("Open",
                    "There was an error opening {0}.".format(prjname),
                    detail=str(e))

    SettingsManager.restore(view.all_views())
    view.visible = True
    rc = app.execute()
    SettingsManager.save(view.all_views())

    return rc


def fatal(msg):
    """
    Display an error message and exit with a return code of 1.

    msg is the text of the message, excluding newlines.
    """
    sys.stderr.write("msipgen: %s\n" % msg)
    sys.exit(1)


def msip_main():
    """ The entry point for the setuptools generated msip wrapper. """

    # Parse the command line.
    parser = argparse.ArgumentParser()
    parser.add_argument('project', help="the project to edit", nargs='?')
    args = parser.parse_args()

    return launchGUI(args.project, sys.argv)


def msipgen_main():
    """ The entry point for the setuptools generated msipgen wrapper. """

    # Parse the command line.
    parser = argparse.ArgumentParser()

    parser.add_argument('project', help="the project to generate code for",
            nargs='?')
    parser.add_argument('-g',
            help="the directory to write the generated code to",
            dest='gendir', metavar='DIR', required=True)
    parser.add_argument('-O', help="generate code for an older version of sip",
            dest='latest_sip', default=True, action='store_false')

    args = parser.parse_args()

    return generate(args.project, args.gendir, args.latest_sip)
