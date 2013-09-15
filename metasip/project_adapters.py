# Copyright (c) 2013 Riverbank Computing Limited.
#
# This file is part of metasip.
#
# This file may be used under the terms of the GNU General Public License v3
# as published by the Free Software Foundation which can be found in the file
# LICENSE-GPL3.txt included in this package.
#
# This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
# WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.


from dip.model import adapt, Adapter, DelegatedTo, observe
from dip.io import IFilterHints
from dip.shell import IManagedModel
from dip.ui import IDisplay

from .Project import Project, Module


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

    @observe('location')
    def __location_changed(self, change):
        """ Invoked when the location changes. """

        self.adaptee.name = str(change.new)


@adapt(Module, to=IDisplay)
class ModuleIDisplayAdapter(Adapter):
    """ Adapt the Module class to the IDisplay interface. """

    name = DelegatedTo('adaptee.name')
