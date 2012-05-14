# Copyright (c) 2012 Riverbank Computing Limited.
#
# This file is part of metasip.
#
# This file may be used under the terms of the GNU General Public License v3
# as published by the Free Software Foundation which can be found in the file
# LICENSE-GPL3.txt included in this package.
#
# This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
# WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.


from dip.model import Model, Str, Trigger


class ScannerModel(Model):
    """ ScannerModel is an internal class representing the project related
    state for the scanner tool.
    """

    # Pulled to delete the selected header directory.
    delete = Trigger()

    # The text displayed when there is no project.
    no_project_text = Str("There is no project to scan.")

    # The file filter to use when scanning the current header directory.
    file_filter = Str()

    # The suffix to be appended to the source directory to create the full name
    # of the current header directory.
    header_directory_suffix = Str()

    # Pulled to create a new header directory.
    new = Trigger()

    # The arguments to pass to the C++ parser when parsing a file in the
    # current header directory..
    parser_arguments = Str()

    # Pulled to mark all header directories as needing to be scanned.
    restart = Trigger()

    # Pulled to scan the current header directory.
    scan = Trigger()

    # The name of the root directory containing all the header file
    # directories.
    source_directory = Str()

    # Pulled to update the project with the modified file filter, header
    # directory suffix and parser arguments.
    update = Trigger()

    # The working version if any versions have been defined.
    working_version = Str(None, allow_none=True)
