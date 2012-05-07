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


from dip.model import Instance, Int, Interface, List, Str

from .i_header_directory import IHeaderDirectory
from .i_module import IModule
from .i_version import IVersion
from .project_version import ProjectVersion


class IProject(Interface):
    """ The IProject interface is implemented by models representing a project.
    """

    # The list of externally defined features.
    externalfeatures = List(Str())

    # The list of externally defined modules.
    externalmodules = List(Str())

    # The list of features.
    features = List(Str())

    # The list of header directories.
    headers = List(IHeaderDirectory)

    # The list of namespaces to ignore.
    ignorednamespaces = List(Str())

    # The list of Python modules.
    modules = List(IModule)

    # The list of platforms.
    platforms = List(Str())

    # The name of the optional root Python module.
    rootmodule = Str()

    # The comments placed at the start of every generated .sip file.
    sipcomments = Str()

    # The version number of the project format.
    version = Int(ProjectVersion)

    # The ordered list of versions.  There will be at least one (whose name
    # will be an empty string if no versions have been explicitly defined).
    versions = List(IVersion)

    # The version being worked on.
    workingversion = Instance(IVersion)
