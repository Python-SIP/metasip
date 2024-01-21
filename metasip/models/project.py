# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


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
