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


from dip.model import adapt, Adapter
from dip.io import IFilterHints
from dip.shell import IManagedModel

from .Project import Project
from .i_project import IProject


@adapt(Project, to=IProject)
class ProjectIProjectAdapter(Adapter):
    """ Adapt the Project class to the IProject interface. """


@adapt(Project, to=IFilterHints)
class ProjectIFilterHintsAdapter(Adapter):
    """ Adapt the Project class to the IFilterHints interface. """

    # The filter.
    filter = "MetaSIP project files (*.msp)"


@adapt(Project, to=IManagedModel)
class ProjectIManagedModelAdapter(Adapter):
    """ Adapt the Project class to the IManagedModel interface. """

    # The native format.
    native_format = 'metasip.formats.project'

    @IManagedModel.dirty.getter
    def dirty(self):
        """ Invoked to get the dirty state. """

        return self.adaptee.hasChanged()

    @dirty.setter
    def dirty(self, value):
        """ Invoked to set the dirty state. """

        # We can only reset the state, which with the current version of dip is
        # all that we will be asked to do.  However check in case this changes
        # in the future.
        if value:
            raise NotImplementedError

        self.adaptee.resetChanged()
