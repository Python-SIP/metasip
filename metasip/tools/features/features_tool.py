# Copyright (c) 2018 Riverbank Computing Limited.
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
        Dialog, IDialog, DialogController, Form, LineEditor, MessageArea, VBox)

from ...interfaces.project import IProject
from ...utils.project import ITagged_items, validate_identifier


@implements(ITool, ISubscriber)
class FeaturesTool(Model):
    """ The FeaturesTool implements a tool for handling a project's set of
    features.
    """

    # The delete feature dialog.
    dialog_delete = Dialog(
            VBox(Form(ComboBox('feature', options='features')),
                    CheckBox('discard',
                            label="Discard any parts of the project that are "
                                    "only enabled for this feature")),
            title="Delete Feature")

    # The new feature dialog.
    dialog_new = Dialog(
            VBox(Form('feature'),
                    CheckBox('external',
                            label="The feature is defined in another project"),
                    MessageArea()),
            title="New Feature")

    # The rename feature dialog.
    dialog_rename = Dialog(
            ComboBox('old_name', label="Feature", options='features'),
            LineEditor('feature', label="New name"), MessageArea(),
            title="Rename Feature")

    # The tool's identifier.
    id = 'metasip.tools.features'

    # The delete feature action.
    feature_delete = Action(enabled=False, text="Delete Feature...")

    # The new feature action.
    feature_new = Action(enabled=False, text="New Feature...")

    # The rename feature action.
    feature_rename = Action(enabled=False, text="Rename Feature...")

    # The collection of the tool's actions.
    features_actions = ActionCollection(text="Features",
            actions=['feature_new', 'feature_rename', 'feature_delete'],
            within='dip.ui.collections.edit')

    # The type of models we subscribe to.
    subscription_type = IProject

    @observe('subscription')
    def __subscription_changed(self, change):
        """ Invoked when the subscription changes. """

        project = change.new.model

        is_active = (change.new.event == 'dip.events.active')
        are_features = (len(project.features) + len(project.externalfeatures) != 0)

        IAction(self.feature_new).enabled = is_active
        IAction(self.feature_rename).enabled = (is_active and are_features)
        IAction(self.feature_delete).enabled = (is_active and are_features)

    @feature_delete.triggered
    def feature_delete(self):
        """ Invoked when the delete feature action is triggered. """

        project = self.subscription.model
        all_features = self._all_features(project)
        model = dict(feature=all_features[0], features=all_features,
                discard=False)

        dlg = self.dialog_delete(model)

        if IDialog(dlg).execute():
            feature = model['feature']
            discard = model['discard']

            # Delete from each API item it appears.
            remove_items = []

            for api_item, container in self._featured_items():
                remove_features = []

                for f in api_item.features:
                    if f[0] == '!':
                        if f[1:] == feature:
                            # Just remove it if it is not the only one or if we
                            # are discarding if enabled (and the feature is
                            # inverted).
                            if len(api_item.features) > 1 or discard:
                                remove_features.append(f)
                            else:
                                remove_items.append((api_item, container))
                                break
                    elif f == feature:
                        # Just remove it if it is not the only one or if we are
                        # discarding if enabled.
                        if len(api_item.features) > 1 or not discard:
                            remove_features.append(f)
                        else:
                            remove_items.append((api_item, container))
                            break
                else:
                    # Note that we deal with a feature appearing multiple
                    # times, even though that is probably a user bug.
                    for f in remove_features:
                        api_item.features.remove(f)

            for api_item, container in remove_items:
                container.content.remove(api_item)

            # Delete from the project's list.
            if feature in project.externalfeatures:
                feature_list = project.externalfeatures
            else:
                feature_list = project.features

            feature_list.remove(feature)
            IDirty(project).dirty = True

            self._update_actions()

    @feature_new.triggered
    def feature_new(self):
        """ Invoked when the new feature action is triggered. """

        project = self.subscription.model
        model = dict(feature='', external=False)

        dlg = self.dialog_new(model,
                controller=FeatureController(project=project))

        if IDialog(dlg).execute():
            feature = model['feature']
            external = model['external']

            if external:
                feature_list = project.externalfeatures
            else:
                feature_list = project.features

            feature_list.append(feature)
            IDirty(project).dirty = True

            self._update_actions()

    @feature_rename.triggered
    def feature_rename(self):
        """ Invoked when the rename feature action is triggered. """

        project = self.subscription.model
        all_features = self._all_features(project)
        model = dict(feature='', old_name=all_features[0],
                features=all_features)

        dlg = self.dialog_rename(model,
                controller=FeatureController(project=project))

        if IDialog(dlg).execute():
            old_name = model['old_name']
            new_name = model['feature']

            # Rename in each API item it appears.
            for api_item, _ in self._featured_items():
                for i, f in enumerate(api_item.features):
                    if f[0] == '!':
                        if f[1:] == old_name:
                            api_item.features[i] = '!' + new_name
                    elif f == old_name:
                        api_item.features[i] = new_name

            # Rename in the project's list.
            if old_name in project.externalfeatures:
                feature_list = project.externalfeatures
            else:
                feature_list = project.features

            feature_list[feature_list.index(old_name)] = new_name
            IDirty(project).dirty = True

    def _update_actions(self):
        """ Update the enabled state of the rename and delete actions. """

        are_features = (len(self.subscription.model.features) != 0)

        IAction(self.feature_rename).enabled = are_features
        IAction(self.feature_delete).enabled = are_features

    @staticmethod
    def _all_features(project):
        """ Return the sorted list of all the features of a project. """

        return sorted(project.features + project.externalfeatures)

    def _featured_items(self):
        """ Returns a list of 2-tuples of all API items that are subject to a
        feature and the API item that contains it.  The list is in depth first
        order.
        """

        # Convert to a list while ignoring featureless items.
        return [item for item in ITagged_items(self.subscription.model) if len(item[0].features) != 0]


class FeatureController(DialogController):
    """ A controller for a dialog containing an editor for a feature. """

    # The project.
    project = Instance(IProject)

    def validate_view(self):
        """ Validate the view. """

        feature = self.feature_editor.value

        message = validate_identifier(feature, "feature")
        if message != "":
            return message

        if feature in self.project.features:
            return "A feature has already been defined with the same name."

        if feature in self.project.externalfeatures:
            return "An external feature has already been defined with the same name."

        return ""
