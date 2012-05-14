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
from dip.shell import IDirty, ITool
from dip.ui import Action, IAction, Application, Dialog, IDialog

from ...interfaces.project import IProject


@implements(ITool, ISubscriber)
class VersionsTool(Model):
    """ The VersionsTool implements a tool for handling a project's explicit
    versions.
    """

    # The versions dialog.
    dialog = Dialog('versions', window_title="Versions")

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

        project = self.subscription.model
        model = dict(versions=project.versions)

        # FIXME: Validate any new entries making sure they are unique and
        #        contain no spaces or hyphens.
        dlg = self.dialog(model)

        if IDialog(dlg).execute():
            # At the moment we only support adding new versions.
            old_versions = project.versions
            new_versions = model['versions']

            new_so_far = 0
            ok = True
            for i, new in enumerate(new_versions):
                try:
                    old_i = old_versions.index(new)

                    if old_i != i + new_so_far:
                        # It's an old version in a different position.
                        ok = False
                        break
                except ValueError:
                    # It's a new version.
                    new_so_far += 1

            if ok:
                # Check that nothing has been deleted.
                if len(old_versions) + new_so_far != len(new_versions):
                    ok = False

            if ok:
                project.versions = new_versions
                IDirty(project).dirty = True
            else:
                Application.warning("Versions",
                        "At the moment only adding new versions is supported",
                        self.shell)
