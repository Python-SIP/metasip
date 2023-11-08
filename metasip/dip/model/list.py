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


from .any import Any
from .attribute_change import AttributeChange
from .change_trigger import get_change_trigger
from .exceptions import ValidationTypeError
from .mutable_type_factory import MutableTypeFactory


# A unique object that is used to determine whether an optional argument was
# given or not.
DefaultArgValue = object()


class List(MutableTypeFactory):
    """ The List class encapsulates a Python list with elements of a
    particular type.
    """

    def __init__(self, element_type=None, default=DefaultArgValue, allow_none=False, allow_rebind=True, getter=None, setter=None, **metadata):
        """ Initialise the object.

        :param element_type:
            the type of each element of the list.  If it is omitted then
            elements of any type are allowed.  If it is a string then it is
            the "full" name of the type.  The string form allows types to be
            specified while avoiding circular imports.
        :param default:
            is the default value of the list.  If is it omitted then an empty
            list is the default.
        :param allow_none:
            ``True`` if ``None`` is a valid value.  The default is ``False``.
        :param allow_rebind:
            ``True`` if the attribute can be re-bound after the model has been
            instantiated.
        :param getter:
            is the optional attribute getter.
        :param setter:
            is the optional attribute setter.
        :param metadata:
            is additional meta-data stored with the type.
        """

        self.element_type = element_type

        if default is DefaultArgValue:
            default = []

        super().__init__(default, allow_none, allow_rebind, getter, setter,
                metadata)

    def copy(self):
        """ Create a copy of this instance.

        :return:
            the copied instance.
        """

        return self.__class__(self.element_type, self.default_value,
                self.allow_none, self.allow_rebind, self.getter_func,
                self.setter_func, **self.metadata)

    def validate(self, value):
        """ Validate a list according to the constraints.  An exception is
        raised if the list is invalid.

        :param value:
            the list to validate.
        :return:
            the validated list.
        """

        if self.validate_none(value):
            return value

        # Make sure the type is resolved.
        self.element_type = self.resolve_type(self.element_type)

        # Allow any iterator.
        if not hasattr(value, '__iter__'):
            raise ValidationTypeError(type(self), list, value)

        return ListImpl(self, self.validated_list(value))

    def validated_list(self, value):
        """ Return a list containing validated elements.

        :param value:
            the list of (possibly) invalid elements.
        :return:
            a corresponding list of validated elements.
        """

        # There is no need to validate an untyped list.
        if self.untyped(self.element_type):
            return value

        # We only need to check the type of a validated list.
        if isinstance(value, ListImpl):
            if not self.untyped(value._dip_element_type):
                self.validate_collection_type(self.element_type,
                        value._dip_element_type)

                return value

        return [self.validate_collection_value(self.element_type, v)
                for v in value]


class ListImpl(list):
    """ The ListImpl class is a list that validates new elements against a
    type.
    """

    def __init__(self, list_type, validated_list):
        """ Initialise the object. """

        self._dip_list_type = list_type
        self._dip_element_type = list_type.element_type
        self._dip_model = None

        super().__init__(validated_list)

    def _dip_changed(self, trigger, new, old):
        """ Notify any change. """

        if new != old:
            trigger.change = AttributeChange(model=self._dip_model,
                    name=self._dip_list_type.name, new=new, old=old)

    def _dip_change_trigger(self):
        """ Return the change trigger if there is one. """

        model = self._dip_model

        return None if model is None else get_change_trigger(model,
                self._dip_list_type.name)

    def append(self, element):
        """ Reimplemented to validate the element. """

        trigger = self._dip_change_trigger()

        element = self._dip_list_type.validate_collection_value(
                self._dip_element_type, element)

        super().append(element)

        if trigger is not None:
            self._dip_changed(trigger, [element], [])

    def extend(self, extension):
        """ Reimplemented to validate the list extension. """

        trigger = self._dip_change_trigger()

        extension = self._dip_list_type.validated_list(extension)

        super().extend(extension)

        if trigger is not None:
            self._dip_changed(trigger, extension, [])

    def insert(self, n, element):
        """ Reimplemented to validate the element. """

        trigger = self._dip_change_trigger()

        element = self._dip_list_type.validate_collection_value(
                self._dip_element_type, element)

        super().insert(n, element)

        if trigger is not None:
            self._dip_changed(trigger, [element], [])

    def pop(self, n=None):
        """ Reimplemented to trigger the change notification. """

        trigger = self._dip_change_trigger()

        if n is None:
            element = super().pop()
        else:
            element = super().pop(n)

        if trigger is not None:
            self._dip_changed(trigger, [], [element])

        return element

    def remove(self, element):
        """ Reimplemented to validate the element. """

        trigger = self._dip_change_trigger()

        element = self._dip_list_type.validate_collection_value(
                self._dip_element_type, element)

        super().remove(element)

        if trigger is not None:
            self._dip_changed(trigger, [], [element])

    def reverse(self):
        """ Reimplemented to trigger the change notification. """

        trigger = self._dip_change_trigger()

        if trigger is not None:
            old = list(self)

        super().reverse()

        if trigger is not None:
            self._dip_changed(trigger, self, old)

    def sort(self, key=None, reverse=0):
        """ Reimplemented to trigger the change notification. """

        trigger = self._dip_change_trigger()

        if trigger is not None:
            old = list(self)

        super().sort(key=key, reverse=reverse)

        if trigger is not None:
            self._dip_changed(trigger, self, old)

    def __iadd__(self, extension):
        """ Reimplemented to validate the list extension. """

        trigger = self._dip_change_trigger()

        if trigger is not None:
            old = list(self)

        extension = self._dip_list_type.validated_list(extension)

        ret = super().__iadd__(extension)

        if trigger is not None:
            self._dip_changed(trigger, ret, old)

        return ret

    def __setitem__(self, key, value):
        """ Reimplemented to validate the value. """

        trigger = self._dip_change_trigger()

        if isinstance(key, slice):
            value = self._dip_list_type.validated_list(value)

            if trigger is not None:
                old = self.__getitem__(key)
                new = value
        else:
            value = self._dip_list_type.validate_collection_value(
                    self._dip_element_type, value)

            if trigger is not None:
                old = [self.__getitem__(key)]
                new = [value]

        super().__setitem__(key, value)

        if trigger is not None:
            self._dip_changed(trigger, new, old)

    def __delitem__(self, n):
        """ Reimplemented to trigger the change notification. """

        trigger = self._dip_change_trigger()

        if trigger is not None:
            if isinstance(n, slice):
                old = self.__getitem__(n)
            else:
                old = [self.__getitem__(n)]

        super().__delitem__(n)

        if trigger is not None:
            self._dip_changed(trigger, [], old)
