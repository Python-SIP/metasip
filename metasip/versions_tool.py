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


from dip.model import implements, Model, observe
from dip.publish import ISubscriber
from dip.shell import ITool
from dip.ui import Action, IAction

from .interfaces.project import IProject


@implements(ITool, ISubscriber)
class VersionsTool(Model):
    """ The VersionsTool implements a tool for handling a project's explicit
    versions.
    """

    # The tool's identifier.
    id = 'metasip.tools.versions'

    # The type of models we subscribe to.
    subscription_type = IProject

    # The action.
    versions_action = Action(id='metasip.actions.versions', enabled=False,
            text="Versions...", within='dip.ui.collections.edit')

    @observe('subscription')
    def __subscription_changed(self, change):
        """ Invoked when the subscription changes. """

        IAction(self.versions_action).enabled = (change.new.event == 'dip.events.active')

    @versions_action.triggered
    def versions_action(self):
        """ Invoked when the versions action is triggered. """

        print("Doing versions")
