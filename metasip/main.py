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

from .exceptions import UserException
from .models import Project
from .project_io import generate_sip_files, load_project
from ._version import version


def main():
    """ The entry point for the msipgen console script. """

    # Parse the command line.
    parser = argparse.ArgumentParser()

    # TODO: use -- long arguments.
    parser.add_argument('-V', '--version', action='version', version=version)
    parser.add_argument('project', help="the project to generate code for",
            nargs='?')
    parser.add_argument('-g',
            help="the directory to write the generated code to",
            dest='output_dir', metavar='DIR', required=True)
    # TODO: change this to a list of modules to ignore - also change rbtools
    parser.add_argument('-m',
            help="the module to generate code for",
            dest='modules', metavar='MODULE', action='append')
    parser.add_argument('--verbose', help="display progress messages",
            dest='verbose', default=False, action='store_true')

    args = parser.parse_args()

    try:
        _generate(args.project, args.modules, args.output_dir, args.verbose)
    except Exception as e:
        _handle_exception(e)


def _generate(project_name, modules, output_dir, verbose):
    """ Generate the .sip files for a project and return an exit code or 0 if
    there was no error.
    """

    if not project_name:
        raise UserException("Specify the name of an existing project file")

    project = Project(project_name)
    load_project(project)

    # TODO: no need to calculate this when passed on the command line.
    ignored_modules = []

    if modules:
        for module in project.modules:
            if module.name not in modules:
                ignored_modules.append(module.name)

    generate_sip_files(project, output_dir, ignored_modules, verbose)


def _handle_exception(e):
    """ Tell the user about an exception. """

    if isinstance(e, UserException):
        # An "expected" exception.
        if e.detail is not None:
            message = "{0}: {1}".format(e.text, e.detail)
        else:
            message = e.text

        print("{0}: {1}".format(os.path.basename(sys.argv[0]), message),
                file=sys.stderr)

        sys.exit(1)

    # An internal error.
    print("{0}: An internal error occurred...".format(
            os.path.basename(sys.argv[0])),
            file=sys.stderr)

    raise e
