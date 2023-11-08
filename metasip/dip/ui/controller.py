# Copyright (c) 2018 Riverbank Computing Limited.
#
# This file is part of dip.
#
# This file may be used under the terms of the GNU General Public License
# version 3.0 as published by the Free Software Foundation and appearing in
# the file LICENSE included in the packaging of this file.  Please review the
# following information to ensure the GNU General Public License version 3.0
# requirements will be met: http://www.gnu.org/copyleft/gpl.html.
#
# If you do not wish to use this file under the terms of the GPL version 3.0
# then you may purchase a commercial license.  For more information contact
# info@riverbankcomputing.com.
#
# This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
# WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.


from functools import partial

from ..model import Bool, Instance, List, Model, observe, Str, ValueTypeFactory

from .i_action import IAction
from .i_container import IContainer
from .i_editor import IEditor
from .i_message_area import IMessageArea
from .i_view import IView


class Controller(Model):
    """ The Controller class is the base implementation of a
    :term:`controller`.
    """

    # The list of actions.
    actions = List(IAction)

    # This determines if the controller should automatically update the model
    # when the user changes the value of an editor.
    auto_update_model = Bool(True)

    # The list of editors being controlled.
    editors = List(IEditor)

    # This explains why the view is invalid.  It will be an empty string if
    # the view is valid.
    invalid_reason = Str()

    # The message areas for giving feedback to the user.
    message_areas = List(IMessageArea)

    # The model.
    model = Instance(Model, allow_rebind=False)

    # The view.
    view = Instance(IView, allow_rebind=False)

    # The action that is currently causing a change to the model.
    _changing_action = Instance(IAction)

    # The editor that is currently causing a change to the model.
    _changing_editor = Instance(IEditor)

    # The list of invalid editors.
    _invalid_editors = List(IEditor)

    # The action that is currently being refreshed from the model.
    _refreshing_action = Instance(IAction)

    # The editor that is currently being refreshed from the model.
    _refreshing_editor = Instance(IEditor)

    def __init__(self):
        """ Initialise the object. """

        super().__init__()

        for view in self.view.all_views():
            # The view may already have a controller.
            if view.controller is None:
                view.controller = self

            # Add any bound editors in the view.
            if isinstance(view, IEditor) and view.attribute_name != '':
                self.editors.append(view)

            # Add any bound actions in the view.
            if isinstance(view, IContainer):
                for action in view.actions:
                    if isinstance(action, IAction) and action.attribute_name != '':
                        self.actions.append(action)

            # Add any message areas.
            if isinstance(view, IMessageArea):
                self.message_areas.append(view)

    def is_valid(self, editor=None):
        """ Return the validity of an editor's (or all editors) current value.

        :param editor:
            is the editor.  If this is ``None`` then the validity of all
            editors is returned.
        :return:
            ``True`` if the editor (or all editors) is valid.
        """

        if editor is None:
            return (self.invalid_reason == '')

        return (editor not in self._invalid_editors)

    def refresh_view(self):
        """ The values of the editors and actions are updated from the model.
        """

        for editor in self.editors:
            if isinstance(editor.attribute_type, ValueTypeFactory):
                # Prevent this triggering a model update.
                self._refreshing_editor = editor
                editor.value = getattr(editor.model, editor.attribute_name)
                self._refreshing_editor = None

        for action in self.actions:
            name = action.attribute_name
            if name == '':
                continue

            # Prevent this triggering a model update.
            self._refreshing_action = action
            action.checked = getattr(action.model, name)
            self._refreshing_action = None

        self.validate()

    def update_model(self):
        """ Update the all the attributes of a model that have a corresponding
        editor or action.
        """

        for editor in self.__valid_editors():
            setattr(editor.model, editor.attribute_name, editor.value)

        for action in self.actions:
            name = action.attribute_name
            if name == '':
                continue

            setattr(editor.model, name, action.checked)

        self.update_view()

    def update_view(self):
        """ This is called after the view has been validated giving the
        controller an opportunity to update the state of the view.  This
        implementation does nothing.
        """

    def validate(self):
        """ Validate the view and update the explanation as to why it is (or
        isn't) invalid.
        """

        self._invalid_editors = []

        invalid_reason = ''

        for editor in self.__valid_editors():
            if editor.validator is not None:
                reason = editor.validator.validate(editor)

                if reason != '':
                    self._invalid_editors.append(editor)

                    if invalid_reason == '':
                        # Remember the first reason.
                        invalid_reason = "{0}: {1}.".format(editor.title,
                                reason)

        if invalid_reason == '':
            invalid_reason = self.validate_view()

        for message_area in self.message_areas:
            message_area.text = invalid_reason

        self.invalid_reason = invalid_reason

        self.update_view()

    def validate_view(self):
        """ This is called after the view has been updated and only if all the
        view's editors contain valid values giving the controller an
        opportunity to carry out cross-editor validation.

        :return:
            a string which will be empty if the view is valid, otherwise it
            will explain why the view is invalid.  This implementation always
            returns an empty string.
        """

        return ''

    @observe('actions')
    def __on_actions_changed(self, change):
        """ Invoked when the list of actions changes. """

        # De-configure any removed actions.
        for action in change.old:
            name = action.attribute_name
            if name == '':
                continue

            model = action.model

            observe('trigger', action,
                    partial(self.__on_action_changed, action=action),
                    remove=True)

            observe(name, model,
                    partial(self.__on_action_attr_changed, action=action),
                    remove=True)

        # Configure any added actions.
        for action in change.new:
            name = action.attribute_name
            if name == '':
                continue

            model = action.model

            # Get the initial checked state.
            action.checked = getattr(model, name)

            # Watch for any subsequent model changes.
            observe(name, model,
                    partial(self.__on_action_attr_changed, action=action))

            # Watch for any action changes.
            observe('trigger', action,
                    partial(self.__on_action_changed, action=action))

    def __on_action_changed(self, change, action):
        """ This is invoked when the user triggers an action. """

        if self._refreshing_action is not action:
            # We will only be called if the action is bound to a model
            # attribute.
            self.validate()

            if self.auto_update_model:
                # Prevent recursive changes.
                self._changing_action = action
                setattr(action.model, action.attribute_name, action.checked)
                self._changing_action = None

    def __on_action_attr_changed(self, change, action):
        """ Invoked when the attribute bound to an action changes. """

        # Don't do anything if this action triggered the change.
        if self._changing_action is not action:
            action.value = change.new

            self.validate()

    @observe('editors')
    def __on_editors_changed(self, change):
        """ Invoked when the list of editors changes. """

        # De-configure any removed editors.
        for editor in change.old:
            observe('value', editor,
                    partial(self.__on_editor_changed, editor=editor),
                    remove=True)

            if isinstance(editor.attribute_type, ValueTypeFactory):
                observe(editor.attribute_name, editor.model,
                        partial(self.__on_editor_attr_changed, editor=editor),
                        remove=True)

            editor.controller = None

        # Configure any added editors.
        for editor in change.new:
            editor.controller = self

            # Do any setup that is specific to types that represent a value.
            if isinstance(editor.attribute_type, ValueTypeFactory):
                # Watch for any subsequent model changes.
                observe(editor.attribute_name, editor.model,
                        partial(self.__on_editor_attr_changed, editor=editor))

            # Watch for any view changes.
            observe('value', editor,
                    partial(self.__on_editor_changed, editor=editor))

    def __on_editor_changed(self, change, editor):
        """ This is invoked when the user changes the value of an editor. """

        if self._refreshing_editor is not editor:
            value = change.new

            if isinstance(editor.attribute_type, ValueTypeFactory):
                self.validate()

                if self.auto_update_model and self.is_valid(editor):
                    # Prevent recursive changes.
                    self._changing_editor = editor
                    setattr(editor.model, editor.attribute_name, value)
                    self._changing_editor = None
            else:
                # Non-value types must update the model immediately.
                setattr(editor.model, editor.attribute_name, value)

    def __on_editor_attr_changed(self, change, editor):
        """ Invoked when the attribute bound to an editor changes. """

        # Don't do anything if this editor triggered the change.
        if self._changing_editor is not editor:
            editor.value = change.new

            self.validate()

    def __valid_editors(self):
        """ Returns a generator of valid editors. """

        for editor in self.editors:
            # Ignore disabled editors as they may legitimately contain invalid
            # values.
            if isinstance(editor.attribute_type, ValueTypeFactory) and editor.enabled:
                yield editor
