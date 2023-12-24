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


from dataclasses import dataclass, field

from .header_directory import HeaderDirectory
from .module import Module
from .project_version import ProjectVersion


@dataclass
class Project:
    """ This class implements a project. """

    # The name of the project file.  Note that this isn't part of the project
    # file itself.
    name: str = ''

    # The dirty state of the project.  Note that this isn't part of the project
    # file itself.
    dirty: bool = False

    # The list of externally defined features.
    externalfeatures: list[str] = field(default_factory=list)

    # The list of externally defined modules.
    externalmodules: list[str] = field(default_factory=list)

    # The list of features.
    features: list[str] = field(default_factory=list)

    # The list of header directories.
    headers: list[HeaderDirectory] = field(default_factory=list)

    # The list of Python modules.
    modules: list[Module] = field(default_factory=list)

    # The list of platforms.
    platforms: list[str] = field(default_factory=list)

    # The name of the optional root Python module.
    rootmodule: str = ''

    # The comments placed at the start of every generated .sip file.
    sipcomments: str = ''

    # The version number of the project format.
    version: tuple[int] = ProjectVersion

    # The ordered list of versions.
    versions: list[str] = field(default_factory=list)
