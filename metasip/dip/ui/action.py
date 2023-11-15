# Copyright (c) 2023 Riverbank Computing Limited.
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


from ..model import (Bool, get_attribute_type, resolve_attribute_path,
        ValidationTypeError, ValueTypeFactory)

from .i_action import IAction
from .toolkits import UIToolkit


class Action(ValueTypeFactory):
    """ The Action class encapsulates an instance of an implementation of
    :class:`~dip.ui.IAction`.  This can be used either to define an
    :term:`attribute type` in a model or to create a factory that then creates
    actions bound to an attribute of a model.
    """

    def __init__(self, bind_to='', id=None, checkable=None, checked=None, enabled=True, shortcut=None, status_tip=None, text=None, tool_tip=None, visible=True, whats_this=None, within='', **metadata):
        """ Initialise the object.

        :param bind_to:
            is the name of the attribute that actions are bound to.  This may
            be an :term:`attribute path`.  This should not be specified when an
            attribute type is being defined.
        :param id:
            is the action's identifier.  It is ignored if the action is being
            bound to an attribute.
        :param checkable:
            is set if the action is checkable.
        :param checked:
            is set if the action is checked.
        :param enabled:
            is set if the action is enabled.
        :param shortcut:
            is the shortcut.
        :param status_tip:
            is the status tip.
        :param text:
            is the text of the action.  If this is not specified it will
            default to the name of the attribute if an attribute type is being
            defined, or the name of the attribute that actions are bound to.
            In both cases any underscores will be replaced by spaces and the
            first letter of each word capitalized.
        :param tool_tip:
            is the tool tip.
        :param visible:
            is set if the action is visible.
        :param whats_this:
            is the "What's This?" help.
        :param within:
            is the identifier of an optional collection of actions that this
            action will be placed within.
        :param metadata:
            is additional meta-data stored with the type.
        """

        self.bind_to = bind_to
        self.id = id

        if checkable is not None:
            self.checkable = checkable
            self.checked = False

            if checkable and checked is not None:
                self.checked = checked
        elif checked is not None:
            self.checkable = True
            self.checked = checked
        else:
            self.checkable = self.checked = False

        self.enabled = enabled
        self.shortcut = shortcut
        self.status_tip = status_tip
        self.text = text
        self.tool_tip = tool_tip
        self.visible = visible
        self.whats_this = whats_this
        self.within = within

        self._triggered_func = None

        super().__init__(None, True, True, None, None, metadata)

    def __call__(self, model):
        """ Create the action.  This behaviour is similar to a view factory.

        :param model:
            is the model.
        :return:
            the action.
        """

        action = self._create_action()

        action.id = self.id if self.id is not None else self.bind_to

        if self.bind_to != '':
            name, submodel = resolve_attribute_path(self.bind_to, model)
            attribute_type = get_attribute_type(submodel, name)
            metadata = attribute_type.metadata

            action.attribute_name = name
            action.model = submodel

            action.checkable = isinstance(attribute_type, Bool)

            if self.shortcut is None:
                action.shortcut = metadata.get('shortcut', "")

            if self.status_tip is None:
                action.status_tip = metadata.get('status_tip', "")

            if self.tool_tip is None:
                action.tool_tip = metadata.get('tool_tip', "")

            if self.whats_this is None:
                action.whats_this = metadata.get('whats_this', "")

            if action.text == '':
                action.text = metadata.get('title', '')

        if action.text == '':
            action.text = self._get_natural_name(action.id)

        action.configure(self.metadata)

        return action

    def bind(self, model, value, rebind=False):
        """ This is called when a model attribute is being bound or rebound.

        :param model:
            is the model.
        :param value:
            is the attribute's new value.
        :param rebind:
            is set if the attribute already has a value.
        """

        super().bind(model, value, rebind)

        if self._triggered_func is not None:
            value.when_triggered = lambda a: self._triggered_func(model)

    def clone(self):
        """ Create a clone of this instance.

        :return:
            the cloned instance.
        """

        clone = super().clone()
        clone._triggered_func = self._triggered_func

        return clone

    def copy(self):
        """ Create a copy of this instance.

        :return:
            the copied instance.
        """

        return self.__class__(bind_to=self.bind_to, id=self.id,
                checkable=self.checkable, checked=self.checked,
                enabled=self.enabled, shortcut=self.shortcut,
                status_tip=self.status_tip, text=self.text,
                tool_tip=self.tool_tip, visible=self.visible,
                whats_this=self.whats_this, within=self.within,
                **self.metadata)

    def get_default_value(self):
        """ Get the type's default value.  This will always be a new
        implementation of IAction.
        """

        action = self._create_action()

        # Use any existing text unless it has been explicitly overridden.  If
        # there is no text then use the attribute name.
        if self.text is None:
            if action.text == '':
                action.text = self._get_natural_name(self.name)

        action.id = self.id if self.id is not None else self.name
        action.configure(self.metadata)

        return action

    def create(self):
        """ Create the action.

        :return:
            the action.
        """

        return IAction(UIToolkit.action(None))

    def _create_action(self):
        """ Create an action configured from this factory except for its id and
        the meta-data.
        """

        action = self.create()

        action.checkable = self.checkable
        action.checked = self.checked
        action.enabled = self.enabled

        if self.shortcut is not None:
            action.shortcut = self.shortcut

        if self.status_tip is not None:
            action.status_tip = self.status_tip

        if self.text is not None:
            action.text = self.text

        if self.tool_tip is not None:
            action.tool_tip = self.tool_tip

        action.visible = self.visible

        if self.whats_this is not None:
            action.whats_this = self.whats_this

        action.within = self.within

        return action

    def validate(self, value):
        """ Validate an instance according to the constraints.  An exception
        is raised if the instance is invalid.

        :param value:
            the instance to validate.
        :return:
            the validated instance.
        """

        if value is not None:
            if IAction(value, exception=False) is None:
                raise ValidationTypeError(type(self), type, value)

        return value

    def triggered(self, triggered_func):
        """ This is used to decorate a method that will be invoked when the
        action is triggered.
        """

        clone = self.clone()
        clone._triggered_func = triggered_func

        return clone

    @classmethod
    def different(cls, value1, value2):
        """ Reimplemented to compare two instances to see if they are
        different.

        :param value1:
            is the first value.
        :param value2:
            is the second value.
        :return:
            ``True`` if the values are different.
        """

        return value1 is not value2

    @staticmethod
    def _get_natural_name(name):
        """ Convert an attribute name to a more natural name.  We don't use
        ViewFactory.get_natural_name() because action text tends to be
        capitalised differently.
        """

        name = name.replace('_', ' ')
        name = name.strip()
        name = name.title()

        return name
