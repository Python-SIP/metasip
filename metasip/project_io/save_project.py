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


from ..exceptions import UserException
from ..models.adapters import adapt

from .indent_file import IndentFile


def save_project(project, ui):
    """ Save a project to its project file.  Return True if there was no error.
    """

    try:
        output = IndentFile.create(project.name, indent=2)
    except UserException as e:
        ui.error_creating_file("Save", e.text, e.detail)
        return False

    adapt(project).save(output)

    output.close()

    return True
