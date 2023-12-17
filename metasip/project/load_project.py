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


from xml.etree import ElementTree

from ..exceptions import UserException
from ..models.adapters import adapt
from ..project_version import MinimumProjectVersion, ProjectVersion


def load_project(self, project, ui=None):
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
        minor_version = self._as_int(root.get('version'))
    else:
        major_version = self._as_int(major_version)
        minor_version = self._as_int(minor_version)

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

    elif version[1] != ProjectVersion[1] and ui is not None:
        if not ui.confirm_minor_version_update(version, ProjectVersion):
            return False

        project.dirty = True

    # Populate the project.
    adapt(project).load(root, ui)

    return True