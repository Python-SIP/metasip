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


from dip.model import Int, Interface, List, Str

from .i_header_directory import IHeaderDirectory
from .i_module import IModule
from .project_version import ProjectVersion


class IProject(Interface):
    """ The IProject interface is implemented by projects. """

    externalfeatures = List(Str())

    externalmodules = List(Str())

    features = Str()

    headers = List(IHeaderDirectory)

    ignorednamespaces = Str()

    inputdir = Str()

    modules = List(IModule)

    outputdir = Str()

    platforms = Str()

    rootmodule = Str()

    sipcomments = Str()

    version = Int(ProjectVersion)

    versions = List(Str())

    webxmldir = Str()
