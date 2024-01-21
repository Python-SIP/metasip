# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


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
