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


import re

from dip.model import implements, Instance, Model, observe
from dip.publish import ISubscriber
from dip.shell import IDirty, ITool
from dip.ui import (Action, IAction, ActionCollection, CheckBox, ComboBox,
        Dialog, IDialog, DialogController, Form, LineEditor, MessageArea, VBox)

from ...interfaces.project import IProject
from ...utils.project import ITagged_items


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
            window_title="Delete Feature")

    # The new feature dialog.
    dialog_new = Dialog('feature', MessageArea(), window_title="New Feature")

    # The rename feature dialog.
    dialog_rename = Dialog(
            ComboBox('old_name', label="Feature", options='features'),
            LineEditor('feature', label="New name"), MessageArea(),
            window_title="Rename Feature")

    # The tool's identifier.
    id = 'metasip.tools.features'

    # The delete feature action.
    feature_delete = Action(enabled=False, text="Delete Feature...")

    # The new feature action.
    feature_new = Action(enabled=False, text="New Feature...")

    # The rename feature action.
    feature_rename = Action(enabled=False, text="Rename Feature...")

    # The collection of the tool's actions.
    features_actions = ActionCollection(
            actions=['feature_new', 'feature_rename', 'feature_delete'],
            within='dip.ui.collections.edit')

    # The type of models we subscribe to.
    subscription_type = IProject

    @observe('subscription')
    def __subscription_changed(self, change):
        """ Invoked when the subscription changes. """

        is_active = (change.new.event == 'dip.events.active')
        are_features = (len(change.new.model.features) != 0)

        IAction(self.feature_new).enabled = is_active
        IAction(self.feature_rename).enabled = (is_active and are_features)
        IAction(self.feature_delete).enabled = (is_active and are_features)

    @feature_delete.triggered
    def feature_delete(self):
        """ Invoked when the delete feature action is triggered. """

        project = self.subscription.model
        model = dict(feature=project.features[0], features=project.features,
                discard=False)

        dlg = self.dialog_delete(model)

        if IDialog(dlg).execute():
            feature = model['feature']
            discard = model['discard']
            print("Deleting feature:", feature, discard)

            # Delete from each API item it sppears.
            for api_item, container in self._featured_items():
                remove = []

                for f in api_item.features:
                    if f[0] == '!':
                        if f[1:] == feature:
                            # Just remove it if it is not the only one or if we
                            # are discarding if enabled (and the feature is
                            # inverted).
                            if len(api_item.features) > 1 or discard:
                                remove.append(f)
                            else:
                                container.content.remove(api_item)
                    elif f == feature:
                        # Just remove it if it is not the only one or if we are
                        # discarding if enabled.
                        if len(api_item.features) > 1 or not discard:
                            remove.append(f)
                        else:
                            container.content.remove(api_item)

                # Note that we deal with a feature appearing multiple times,
                # even though that is probably a user bug.
                for f in remove:
                    api_item.features.remove(f)

            # Delete from the project's list.
            project.features.remove(feature)
            IDirty(project).dirty = True

            self._update_actions()

    @feature_new.triggered
    def feature_new(self):
        """ Invoked when the new feature action is triggered. """

        project = self.subscription.model
        model = dict(feature='')

        dlg = self.dialog_new(model,
                controller=FeatureController(project=project))

        if IDialog(dlg).execute():
            project.features.append(model['feature'])
            IDirty(project).dirty = True

            self._update_actions()

    @feature_rename.triggered
    def feature_rename(self):
        """ Invoked when the rename feature action is triggered. """

        project = self.subscription.model
        model = dict(feature='', old_name=project.features[0],
                features=project.features)

        dlg = self.dialog_rename(model,
                controller=FeatureController(project=project))

        if IDialog(dlg).execute():
            old_name = model['old_name']
            new_name = model['feature']

            # Rename in each API item it sppears.
            for api_item, _ in self._featured_items():
                for i, f in enumerate(api_item.features):
                    if f[0] == '!':
                        if f[1:] == old_name:
                            api_item.features[i] = '!' + new_name
                    elif f == old_name:
                        api_item.features[i] = new_name

            # Rename in the project's list.
            project.features[project.features.index(old_name)] = new_name
            IDirty(project).dirty = True

    def _update_actions(self):
        """ Update the enabled state of the rename and delete actions. """

        are_features = (len(self.subscription.model.features) != 0)

        IAction(self.feature_rename).enabled = are_features
        IAction(self.feature_delete).enabled = are_features

    def _featured_items(self):
        """ Returns a list of 2-tuples of all API items that are subject to a
        feature and the API item that contains it.  The list is in depth first
        order.
        """

        # Convert to a list while ignoring featureless items.
        return [item for item in ITagged_items(self.subscription.model) if len(item[0].features) != 0]


class FeatureController(DialogController):
    """ A controller for a dialog containing an editor for a feature. """

    # The regular expression for a valid feature name.
    feature_re = re.compile(r'[_A-Z][_A-Z0-9]*', re.ASCII|re.IGNORECASE)

    # The project.
    project = Instance(IProject)

    def validate_view(self):
        """ Validate the view. """

        feature = self.feature_editor.value

        if feature == '':
            return "A feature name is required."

        if not self.feature_re.match(feature):
            return "A feature name can only contain underscores, ASCII letters and digits and cannot start with a digit."

        if feature in self.project.features:
            return "A feature has already been defined with the same name."

        if feature in self.project.externalfeatures:
            return "An external feature has already been defined with the same name."

        return ""
