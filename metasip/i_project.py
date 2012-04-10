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


from dip.model import adapt, Adapter, Interface

from .Project import Project


class IProject(Interface):
    """ The IProject interface is implemented by projects.  At the moment it is
    just a marker class.
    """


@adapt(Project, to=IProject)
class ProjectIProjectAdapter(Adapter):
    """ Adapt the legacy Project class to the IProject interface. """
