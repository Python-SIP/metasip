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


from dip.model import implements, Model
from dip.ui import IDisplay


@implements(IDisplay)
class ProjectFactory(Model):
    """ A Project factory that implements the IDisplay interface. """

    # The model type name used in model manager dialogs and wizards.
    name = "MetaSIP project"

    def __call__(self):
        """ Invoked to create a project instance. """

        from .Project import Project

        return Project()
