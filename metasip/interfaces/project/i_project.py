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


from ...dip.model import Instance, Int, Interface, List, Str, Tuple

from .i_header_directory import IHeaderDirectory
from .i_module import IModule


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
    version = Tuple(Int())

    # The ordered list of versions.
    versions = List(Str())
