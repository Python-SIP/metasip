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


from ...dip.model import implements, Model, observe
from ...dip.publish import ISubscriber
from ...dip.shell import IDirty, ITool
from ...dip.ui import (Action, IAction, ActionCollection, Application,
        CheckBox, ComboBox, Dialog, IDialog, DialogController, LineEditor,
        MessageArea)

from ...interfaces.project import IProject
from ...utils.project import ITagged_items, validate_identifier

# FIXME: We should not need to know about the actual IProject implementation.
from ...project import HeaderFileVersion


class VersionController(DialogController):
    """ A controller for a dialog containing an editor for a version. """

    def validate_view(self):
        """ Validate the view. """

        version = self.view.version.value

        message = validate_identifier(version, "version")
        if message != "":
            return message

        if version in self.model.project.versions:
            return "A version has already been defined with the same name."

        return ""


@implements(ITool, ISubscriber)
class VersionsTool(Model):
    """ The VersionsTool implements a tool for handling a project's set of
    versions.
    """

    # The delete version dialog.
    dialog_delete = Dialog(ComboBox('version', options='versions'),
            title="Delete Version")

    # The new version dialog.
    dialog_new = Dialog('version',
            ComboBox('after', label="Add version after", options='versions'),
            MessageArea(), title="New Version",
            controller_factory=VersionController)

    # The rename version dialog.
    dialog_rename = Dialog(
            ComboBox('old_name', label="Version", options='versions'),
            LineEditor('version', label="New name"), MessageArea(),
            title="Rename Version", controller_factory=VersionController)

    # The tool's identifier.
    id = 'metasip.tools.versions'

    # The delete version action.
    version_delete = Action(enabled=False, text="Delete Version...")

    # The delete all versions action.
    version_delete_all = Action(enabled=False, text="Delete All Versions")

    # The new version action.
    version_new = Action(text="New Version...")

    # The rename version action.
    version_rename = Action(enabled=False, text="Rename Version...")

    # The collection of the tool's actions.
    versions_actions = ActionCollection(text="Versions",
            actions=['version_new', 'version_rename', 'version_delete',
                    'version_delete_all'],
            within='dip.ui.collections.edit')

    # The type of models we subscribe to.
    subscription_type = IProject

    @observe('subscription')
    def __subscription_changed(self, change):
        """ Invoked when the subscription changes. """

        are_versions = (len(change.new.model.versions) != 0)

        IAction(self.version_rename).enabled = are_versions
        IAction(self.version_delete).enabled = are_versions
        IAction(self.version_delete_all).enabled = are_versions

    @version_delete.triggered
    def version_delete(self):
        """ Invoked when the delete version action is triggered. """

        project = self.subscription.model
        versions = project.versions
        model = dict(version=versions[0], versions=versions)

        dlg = self.dialog_delete(model)

        if IDialog(dlg).execute():
            self._delete_version(model['version'], migrate_items=True)
            self._update_actions()

    @version_delete_all.triggered
    def version_delete_all(self):
        """ Invoked when the delete all versions action is triggered. """

        # Check with the user.
        answer = Application.question(
                IAction(self.version_delete_all).plain_text,
                "All versions will be removed along with any API items that "
                "are not part of the latest version.\n\nDo you wish to "
                "continue?")

        if answer == 'yes':
            for version in list(self.subscription.model.versions):
                self._delete_version(version, migrate_items=False)

            self._update_actions()

    @version_new.triggered
    def version_new(self):
        """ Invoked when the new version action is triggered. """

        project = self.subscription.model
        versions = project.versions
        model = dict(project=project, version='',
                after=versions[-1] if len(versions) > 1 else None,
                versions=versions)

        dlg = self.dialog_new(model)

        dlg.after.visible = (len(versions) > 1)

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
        model = dict(project=project, version='', old_name=project.versions[0],
                versions=project.versions)

        dlg = self.dialog_rename(model)

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

    def _delete_version(self, version, *, migrate_items):
        """ Delete a version and all API items defined by it. """

        project = self.subscription.model
        versions = project.versions

        removing_first_version = (version == versions[0])

        # Delete from each API item it appears.
        remove_items = []

        for api_item, container in self._versioned_items():
            remove_ranges = []

            for r in api_item.versions:
                if r.startversion == version:
                    # It now starts with the version after the one we are
                    # deleting.  If that is the same as the end version then we
                    # delete the API item.
                    new_start = '' if versions[-1] == version else versions[versions.index(version) + 1]

                    if new_start == r.endversion:
                        remove_items.append((api_item, container))
                        break

                    r.startversion = new_start

                # If the start version is now what the first version will now
                # be then we clear it.
                if r.startversion != '' and removing_first_version and r.startversion == versions[1]:
                    r.startversion = ''

                if r.endversion == version:
                    if migrate_items:
                        # It now ends with the version after the one we are
                        # deleting.
                        new_end = '' if versions[-1] == version else versions[versions.index(version) + 1]

                        r.endversion = new_end
                    else:
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
            if version in hdir.scan:
                hdir.scan.remove(version)

            # If the versions to scan now just has a marker from when no
            # versions were defined, remove the marker so it doesn't suggest
            # that any remaining version needs scanning.
            if len(hdir.scan) == 1 and hdir.scan[0] == '':
                del hdir.scan[0]

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

    def _update_actions(self):
        """ Update the enabled state of the rename and delete actions. """

        are_versions = (len(self.subscription.model.versions) != 0)

        IAction(self.version_rename).enabled = are_versions
        IAction(self.version_delete).enabled = are_versions
        IAction(self.version_delete_all).enabled = are_versions

    def _versioned_items(self):
        """ Returns a list of 2-tuples of all API items that are subject to a
        version and the API item that contains it.  The list is in depth first
        order.
        """

        # Convert to a list while ignoring version-less items.
        return [item for item in ITagged_items(self.subscription.model) if len(item[0].versions) != 0]
