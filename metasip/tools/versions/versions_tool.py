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


from dip.model import implements, Instance, Model, observe
from dip.publish import ISubscriber
from dip.shell import IDirty, ITool
from dip.ui import (Action, IAction, ActionCollection, CheckBox, ComboBox,
        Dialog, IDialog, DialogController, LineEditor, MessageArea)

from ...interfaces.project import IProject
from ...utils.project import ITagged_items, validate_identifier

# FIXME: We should not need to know about the actual IProject implementation.
from ...Project import HeaderFileVersion


@implements(ITool, ISubscriber)
class VersionsTool(Model):
    """ The VersionsTool implements a tool for handling a project's set of
    versions.
    """

    # The delete version dialog.
    dialog_delete = Dialog(ComboBox('version', options='versions'),
            window_title="Delete Version")

    # The new version dialog.
    dialog_new = Dialog('version',
            ComboBox('after', label="Add version after", options='versions'),
            MessageArea(), window_title="New Version")

    # The rename version dialog.
    dialog_rename = Dialog(
            ComboBox('old_name', label="Version", options='versions'),
            LineEditor('version', label="New name"), MessageArea(),
            window_title="Rename Version")

    # The tool's identifier.
    id = 'metasip.tools.versions'

    # The delete version action.
    version_delete = Action(enabled=False, text="Delete Version...")

    # The new version action.
    version_new = Action(enabled=False, text="New Version...")

    # The rename version action.
    version_rename = Action(enabled=False, text="Rename Version...")

    # The collection of the tool's actions.
    versions_actions = ActionCollection(
            actions=['version_new', 'version_rename', 'version_delete'],
            within='dip.ui.collections.edit')

    # The type of models we subscribe to.
    subscription_type = IProject

    @observe('subscription')
    def __subscription_changed(self, change):
        """ Invoked when the subscription changes. """

        is_active = (change.new.event == 'dip.events.active')
        are_versions = (len(change.new.model.versions) != 0)

        IAction(self.version_new).enabled = is_active
        IAction(self.version_rename).enabled = (is_active and are_versions)
        IAction(self.version_delete).enabled = (is_active and are_versions)

    @version_delete.triggered
    def version_delete(self):
        """ Invoked when the delete version action is triggered. """

        project = self.subscription.model
        versions = project.versions
        model = dict(version=versions[0], versions=versions)

        dlg = self.dialog_delete(model)

        if IDialog(dlg).execute():
            version = model['version']

            # Delete from each API item it appears.
            remove_items = []

            for api_item, container in self._versioned_items():
                remove_ranges = []

                for r in api_item.versions:
                    remove_item = False

                    if r.startversion == version:
                        # It now starts with the version after the one we are
                        # deleting.  If that is the same as the end version
                        # then we delete the API item.
                        new_start = '' if versions[-1] == version else versions[versions.index(version) + 1]

                        if new_start == r.endversion:
                            remove_item = True
                        else:
                            r.startversion = new_start

                    # If the start version is now what the first version will
                    # now be then we clear it.
                    if r.startversion != '' and r.startversion == versions[1]:
                        r.startversion = ''

                    if r.endversion == version:
                        # It now ends with the version after the one we are
                        # deleting.
                        new_end = '' if versions[-1] == version else versions[versions.index(version) + 1]

                        r.endversion = new_end

                    # If the end version is now what the first version will now
                    # be then we delete the API item.
                    if r.endversion != '' and r.endversion == versions[1]:
                        remove_item = True

                    if remove_item:
                        remove_items.append((api_item, container))
                        break

                    if r.startversion == '' and r.endversion == '':
                        remove_ranges.append(r)
                else:
                    for r in remove_ranges:
                        api_item.versions.remove(r)

            for api_item, container in remove_items:
                container.content.remove(api_item)

            # Delete from the header file versions.
            remove_hfile_versions = []
            removing_last_version = (len(project.versions) == 1)

            for hdir in project.headers:
                for hfile in hdir.content:
                    if removing_last_version:
                        if len(hfile.versions) != 0:
                            hfile.versions[0].version = ''
                    else:
                        for hfile_version in hfile.versions:
                            if hfile_version.version == version:
                                remove_hfile_versions.append((hfile_version, hfile))
                                break

            for hfile_version, hfile in remove_hfile_versions:
                hfile.versions.remove(hfile_version)

            # Delete from the project's list.
            versions.remove(version)
            IDirty(project).dirty = True

            self._update_actions()

    @version_new.triggered
    def version_new(self):
        """ Invoked when the new version action is triggered. """

        project = self.subscription.model
        versions = project.versions
        model = dict(version='',
                after=versions[-1] if len(versions) > 1 else None,
                versions=versions)

        controller=VersionController(project=project)
        dlg = self.dialog_new(model, controller=controller)

        controller.after_editor.visible = (len(versions) > 1)

        if IDialog(dlg).execute():
            version = model['version']
            after = model['after']

            # Add to the header file versions.
            if len(versions) == 0:
                # The first explicit version has been defined.
                for hdir in project.headers:
                    for hfile in hdir.content:
                        # There will only be one version at most defined.
                        if len(hfile.versions) != 0:
                            hfile.versions[0].version = version
            elif after is not None:
                # Create a new header file version based on the previous one.
                for hdir in project.headers:
                    scan = False

                    for hfile in hdir.content:
                        for hfile_version in hfile.versions:
                            if hfile_version == after:
                                new_hfile_version = HeaderFileVersion(
                                        md5=hfile_version.md5, parse=False,
                                        version=version)
                                hfile.versions.append(new_hfile_version)

                                # The header directory needs scanning.
                                scan = True

                                break

                    if scan:
                        hdir.scan.append(version)

            if after is None or after == versions[-1]:
                versions.append(version)
            else:
                versions.insert(versions.index(after) + 1, version)

            IDirty(project).dirty = True

            self._update_actions()

    @version_rename.triggered
    def version_rename(self):
        """ Invoked when the rename version action is triggered. """

        project = self.subscription.model
        model = dict(version='', old_name=project.versions[0],
                versions=project.versions)

        dlg = self.dialog_rename(model,
                controller=VersionController(project=project))

        if IDialog(dlg).execute():
            old_name = model['old_name']
            new_name = model['version']

            # Rename in each API item it appears.
            for api_item, _ in self._versioned_items():
                for r in api_item.versions:
                    if r.startversion == old_name:
                        r.startversion = new_name

                    if r.endversion == old_name:
                        r.endversion = new_name

            # Rename in the header file versions.
            for hdir in project.headers:
                for hfile in hdir.content:
                    for hfile_version in hfile.versions:
                        if hfile_version.version == old_name:
                            hfile_version.version = new_name

            # Rename in the project's list.
            project.versions[project.versions.index(old_name)] = new_name
            IDirty(project).dirty = True

    def _update_actions(self):
        """ Update the enabled state of the rename and delete actions. """

        are_versions = (len(self.subscription.model.versions) != 0)

        IAction(self.version_rename).enabled = are_versions
        IAction(self.version_delete).enabled = are_versions

    def _versioned_items(self):
        """ Returns a list of 2-tuples of all API items that are subject to a
        version and the API item that contains it.  The list is in depth first
        order.
        """

        # Convert to a list while ignoring version-less items.
        return [item for item in ITagged_items(self.subscription.model) if len(item[0].versions) != 0]


class VersionController(DialogController):
    """ A controller for a dialog containing an editor for a version. """

    # The project.
    project = Instance(IProject)

    def validate_view(self):
        """ Validate the view. """

        version = self.version_editor.value

        message = validate_identifier(version, "version")
        if message != "":
            return message

        if version in self.project.versions:
            return "A version has already been defined with the same name."

        return ""
