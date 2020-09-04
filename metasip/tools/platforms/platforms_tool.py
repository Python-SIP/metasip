# Copyright (c) 2020 Riverbank Computing Limited.
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
from dip.ui import (Action, IAction, ActionCollection, CheckBox, ComboBox,
        Dialog, IDialog, DialogController, Form, LineEditor, MessageArea, VBox)

from ...interfaces.project import IProject
from ...utils.project import ITagged_items, validate_identifier


class PlatformController(DialogController):
    """ A controller for a dialog containing an editor for a platform. """

    def validate_view(self):
        """ Validate the view. """

        platform = self.view.platform.value

        message = validate_identifier(platform, "platform")
        if message != "":
            return message

        if platform in self.model.project.platforms:
            return "A platform has already been defined with the same name."

        return ""


@implements(ITool, ISubscriber)
class PlatformsTool(Model):
    """ The PlatformsTool implements a tool for handling a project's set of
    platforms.
    """

    # The delete platform dialog.
    dialog_delete = Dialog(
            VBox(Form(ComboBox('platform', options='platforms')),
                    CheckBox('discard',
                            label="Discard any parts of the project that are "
                                    "only enabled for this platform")),
            title="Delete Platform")

    # The new platform dialog.
    dialog_new = Dialog('platform', MessageArea(), title="New Platform",
            controller_factory=PlatformController)

    # The rename platform dialog.
    dialog_rename = Dialog(
            ComboBox('old_name', label="Platform", options='platforms'),
            LineEditor('platform', label="New name"), MessageArea(),
            title="Rename Platform", controller_factory=PlatformController)

    # The tool's identifier.
    id = 'metasip.tools.platforms'

    # The delete platform action.
    platform_delete = Action(enabled=False, text="Delete Platform...")

    # The new platform action.
    platform_new = Action(text="New Platform...")

    # The rename platform action.
    platform_rename = Action(enabled=False, text="Rename Platform...")

    # The collection of the tool's actions.
    platforms_actions = ActionCollection(text="Platforms",
            actions=['platform_new', 'platform_rename', 'platform_delete'],
            within='dip.ui.collections.edit')

    # The type of models we subscribe to.
    subscription_type = IProject

    @observe('subscription')
    def __subscription_changed(self, change):
        """ Invoked when the subscription changes. """

        are_platforms = (len(change.new.model.platforms) != 0)

        IAction(self.platform_rename).enabled = are_platforms
        IAction(self.platform_delete).enabled = are_platforms

    @platform_delete.triggered
    def platform_delete(self):
        """ Invoked when the delete platform action is triggered. """

        project = self.subscription.model
        model = dict(platform=project.platforms[0],
                platforms=project.platforms, discard=False)

        dlg = self.dialog_delete(model)

        if IDialog(dlg).execute():
            platform = model['platform']
            discard = model['discard']

            # Delete from each API item it appears.
            remove_items = []

            for api_item, container in self._platformed_items():
                remove_platforms = []

                for p in api_item.platforms:
                    if p[0] == '!':
                        if p[1:] == platform:
                            # Just remove it if it is not the only one or if we
                            # are discarding if enabled (and the platform is
                            # inverted).
                            if len(api_item.platforms) > 1 or discard:
                                remove_platforms.append(p)
                            else:
                                remove_items.append((api_item, container))
                                break
                    elif p == platform:
                        # Just remove it if it is not the only one or if we are
                        # discarding if enabled.
                        if len(api_item.platforms) > 1 or not discard:
                            remove_platforms.append(p)
                        else:
                            remove_items.append((api_item, container))
                            break
                else:
                    # Note that we deal with a platform appearing multiple
                    # times, even though that is probably a user bug.
                    for p in remove_platforms:
                        api_item.platforms.remove(p)

            for api_item, container in remove_items:
                container.content.remove(api_item)

            # Delete from the project's list.
            project.platforms.remove(platform)
            IDirty(project).dirty = True

            self._update_actions()

    @platform_new.triggered
    def platform_new(self):
        """ Invoked when the new platform action is triggered. """

        project = self.subscription.model
        model = dict(project=project, platform='')

        dlg = self.dialog_new(model)

        if IDialog(dlg).execute():
            project.platforms.append(model['platform'])
            IDirty(project).dirty = True

            self._update_actions()

    @platform_rename.triggered
    def platform_rename(self):
        """ Invoked when the rename platform action is triggered. """

        project = self.subscription.model
        model = dict(project=project, platform='',
                old_name=project.platforms[0], platforms=project.platforms)

        dlg = self.dialog_rename(model)

        if IDialog(dlg).execute():
            old_name = model['old_name']
            new_name = model['platform']

            # Rename in each API item it appears.
            for api_item, _ in self._platformed_items():
                for i, p in enumerate(api_item.platforms):
                    if p[0] == '!':
                        if p[1:] == old_name:
                            api_item.platforms[i] = '!' + new_name
                    elif p == old_name:
                        api_item.platforms[i] = new_name

            # Rename in the project's list.
            project.platforms[project.platforms.index(old_name)] = new_name
            IDirty(project).dirty = True

    def _update_actions(self):
        """ Update the enabled state of the rename and delete actions. """

        are_platforms = (len(self.subscription.model.platforms) != 0)

        IAction(self.platform_rename).enabled = are_platforms
        IAction(self.platform_delete).enabled = are_platforms

    def _platformed_items(self):
        """ Returns a list of 2-tuples of all API items that are subject to a
        platform and the API item that contains it.  The list is in depth first
        order.
        """

        # Convert to a list while ignoring platform-less items.
        return [item for item in ITagged_items(self.subscription.model) if len(item[0].platforms) != 0]
