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
from .project import Project


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

    try:
        _generate(args.project, args.modules, args.output_dir, args.latest_sip)
    except Exception as e:
        _handle_exception(e)


def _generate(project_name, modules, output_dir, latest_sip):
    """ Generate the .sip files for a project and return an exit code or 0 if
    there was no error.
    """

    if not os.path.isdir(output_dir):
        raise UserException(f"{output_dir} is not an existing directory")

    if not project_name:
        raise UserException("Specify the name of an existing project file")

    project = Project.factory(project_name)

    if modules:
        gen_modules = []

        for module_name in modules:
            for module in project.modules:
                if module.name == module_name:
                    gen_modules.append(module)
                    break
            else:
                raise UserException(
                        f"There is no module '{module_name}' in the project")
    else:
        gen_modules = project.modules

    # Generate each module.
    for module in gen_modules:
        project.generate_module(module, output_dir, latest_sip=latest_sip)


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
    print(
            "{0}: An internal error occurred...".format(
                    os.path.basename(sys.argv[0])),
            file=sys.stderr)

    raise e
