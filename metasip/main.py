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
import os

from .dip.io import IoManager, StorageError
from .dip.io.storage.filesystem import FilesystemStorageFactory

from . import Project, ProjectCodec


def main():
    """ The entry point for the msipgen console script. """

    # Parse the command line.
    parser = argparse.ArgumentParser()

    parser.add_argument('project', help="the project to generate code for",
            nargs='?')
    parser.add_argument('-g',
            help="the directory to write the generated code to",
            dest='output_dir', metavar='DIR', required=True)
    parser.add_argument('-m',
            help="the module to generated code for",
            dest='modules', metavar='MODULE', action='append')
    parser.add_argument('-O', help="generate code for an older version of sip",
            dest='latest_sip', default=True, action='store_false')

    args = parser.parse_args()

    return _generate(args.project, args.modules, args.output_dir,
            args.latest_sip)


def _generate(project_name, modules, output_dir, latest_sip):
    """ Generate the .sip files for a project and return an exit code or 0 if
    there was no error.
    """

    # Configure the i/o manager for reading and writing projects to the
    # filesystem.
    IoManager.codecs.append(ProjectCodec())
    IoManager.storage_factories.append(FilesystemStorageFactory())

    if not os.path.isdir(output_dir):
        _fatal(f"{output_dir} is not an existing directory")

    project = _load_project(project_name)

    if modules:
        gen_modules = []

        for module_name in modules:
            for mod in project.modules:
                if mod.name == module_name:
                    gen_modules.append(mod)
                    break
            else:
                _fatal(f"There is no module '{module_name}' in the project")
    else:
        gen_modules = project.modules

    # Generate each module.
    for mod in gen_modules:
        if not project.generateModule(mod, output_dir, latest_sip=latest_sip):
            _fatal(project.diagnostic)

    # No error if we have got this far.
    return 0


def _load_project(project_name):
    """ Load an existing project. """

    if not project_name:
        _fatal("Specify the name of an existing project file")

    try:
        project = IoManager.read(Project(), project_name,
                'metasip.formats.project')
    except StorageError as e:
        _fatal(e.error)

    return project


def _fatal(msg):
    """ Display an error message and exit with a return code of 1. """

    sys.stderr.write(f"msipgen: {msg}\n")
    sys.exit(1)
