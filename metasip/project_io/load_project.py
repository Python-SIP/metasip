# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


from xml.etree import ElementTree

from ..exceptions import UserException
from ..models import MinimumProjectVersion, ProjectVersion
from ..models.adapters import adapt


def load_project(project, ui=None):
    """ Populate a project from its project file.  Return True if the user
    didn't cancel.
    """

    # Load the file.
    tree = ElementTree.parse(project.name)

    # Do some basic sanity checks.
    root = tree.getroot()

    major_version = root.get('majorversion')
    minor_version = root.get('minorversion')

    if major_version is None and minor_version is None:
        major_version = 0
        minor_version = _as_int(root.get('version'))
    else:
        major_version = _as_int(major_version)
        minor_version = _as_int(minor_version)

    if root.tag != 'Project' or major_version < 0 or minor_version < 0:
        raise UserException(
                f"{project.name} doesn't appear to be a valid metasip project")

    # Check we handle the version.
    version = (major_version, minor_version)

    if version < MinimumProjectVersion:
        raise UserException(
                f"{project.name} was created with an unsupported version of metasip")

    if version > ProjectVersion:
        raise UserException(
                f"{project.name} was created with a later version of metasip")

    # See if user input is required.
    if version[0] != ProjectVersion[0]:
        if ui is None:
            raise UserException(
                    f"{project.name} was created with an earlier version of metasip and must be updated using the GUI")

        if not ui.update_project_format(root, version, ProjectVersion):
            return False

        project.dirty = True

    elif version[1] != ProjectVersion[1]:
        if ui is not None:
            ui.warn_minor_version_update(version, ProjectVersion)

        project.version = version

    # Populate the project.
    adapt(project).load(root, project, ui)

    return True


def _as_int(s):
    """ Return an int from a string or -1 if the string is invalid. """

    try:
        return int(s)
    except ValueError:
        return -1
