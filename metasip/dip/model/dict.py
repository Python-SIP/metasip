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


class Dict(MutableTypeFactory):
    """ The Dict class encapsulates a Python dictionary with keys and values
    of particular types.
    """

    def __init__(self, key_type=None, value_type=None, default=DefaultArgValue, allow_none=False, allow_rebind=True, getter=None, setter=None, **metadata):
        """ Initialise the object.

        :param key_type:
            the type of each key of the dictionary.  If it is omitted then
            keys of any type are allowed.  If it is a string then it is
            the "full" name of the type.  The string form allows types to be
            specified while avoiding circular imports.
        :param value_type:
            the type of each value of the dictionary.  If it is omitted then
            values of any type are allowed.  If it is a string then it is
            the "full" name of the type.  The string form allows types to be
            specified while avoiding circular imports.
        :param default:
            is the default value of the dictionary.  If is it omitted then an
            empty dictionary is the default.
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

        self.key_type = key_type
        self.value_type = value_type

        if default is DefaultArgValue:
            default = {}

        super().__init__(default, allow_none, allow_rebind, setter, getter,
                metadata)

    def copy(self):
        """ Create a copy of this instance.

        :return:
            the copied instance.
        """

        return self.__class__(self.key_type, self.value_type,
                self.default_value, self.allow_none, self.allow_rebind,
                self.getter_func, self.setter_func, **self.metadata)

    def validate(self, value):
        """ Validate a dictionary according to the constraints.  An exception
        is raised if the dictionary is invalid.

        :param value:
            the dictionary to validate.
        :return:
            the validated dictionary.
        """

        if self.validate_none(value):
            return value

        # Make sure the key and value types are resolved.
        self.key_type = self.resolve_type(self.key_type, "key")
        self.value_type = self.resolve_type(self.value_type, "value")

        if not isinstance(value, dict):
            raise ValidationTypeError(type(self), dict, value)

        return DictImpl(self, self.validated_dict(value))

    def validated_dict(self, value):
        """ Return a dictionary containing validated keys and values.

        :param value:
            the dictionary of (possibly) invalid keys and values.
        :return:
            a corresponding dictionary of validated keys and values.
        """

        # There is no need to validate an untyped dictionary.
        key_untyped = self.untyped(self.key_type)
        value_untyped = self.untyped(self.value_type)

        if key_untyped and value_untyped:
            return value

        # We only need to check the types of a validated dict.
        if isinstance(value, DictImpl):
            if key_untyped or self.untyped(value._dip_key_type):
                pass
            elif value_untyped or self.untyped(value._dip_value_type):
                pass
            else:
                self.validate_collection_type(self.key_type,
                        value._dip_key_type, "key")

                self.validate_collection_type(self.value_type,
                        value._dip_value_type, "value")

                return value

        return {self.validate_collection_value(self.key_type, k):
                self.validate_collection_value(self.value_type, v)
                for k, v in value.items()}


class DictImpl(dict):
    """ The DictImpl class is a dictionary that validates new keys and values
    against corresponding types.
    """

    def __init__(self, dict_type, validated_dict):
        """ Initialise the object. """

        self._dip_dict_type = dict_type
        self._dip_key_type = dict_type.key_type
        self._dip_value_type = dict_type.value_type
        self._dip_model = None

        super().__init__(validated_dict)

    def _dip_changed(self, trigger, new, old):
        """ Notify any change. """

        if new != old:
            trigger.change = AttributeChange(model=self._dip_model,
                    name=self._dip_dict_type.name, new=new, old=old)

    def _dip_change_trigger(self):
        """ Return the change trigger if there is one. """

        model = self._dip_model

        return None if model is None else get_change_trigger(model,
                self._dip_dict_type.name)

    def clear(self):
        """ Reimplemented to trigger the change notification. """

        trigger = self._dip_change_trigger()

        if trigger is not None:
            old = dict(self)

        super().clear()

        if trigger is not None:
            self._dip_changed(trigger, {}, old)

    def pop(self, key, value=DefaultArgValue):
        """ Reimplemented to trigger the change notification. """

        trigger = self._dip_change_trigger()

        if value is DefaultArgValue:
            popped = super().pop(key)

            if trigger is not None:
                old = {key: popped}
        else:
            old_size = len(self)

            popped = super().pop(key, value)

            if trigger is not None:
                if old_size != len(self):
                    old = {key: popped}
                else:
                    # Nothing was actually popped.
                    old = {}

        if trigger is not None:
            self._dip_changed(trigger, {}, old)

        return popped

    def popitem(self):
        """ Reimplemented to trigger the change notification. """

        trigger = self._dip_change_trigger()

        popped = super().popitem()

        if trigger is not None:
            key, value = popped
            self._dip_changed(trigger, {}, {key: value})

        return popped

    def setdefault(self, key, value=None):
        """ Reimplemented to validate the new key/value. """

        trigger = self._dip_change_trigger()

        key = self._dip_dict_type.validate_collection_value(self._dip_key_type,
                key)
        value = self._dip_dict_type.validate_collection_value(
                self._dip_value_type, value)

        old_size = len(self)

        value = super().setdefault(key, value)

        if trigger is not None and old_size != len(self):
            self._dip_changed(trigger, {key: value}, {})

        return value

    def update(self, other):
        """ Reimplemented to validate the new key/values. """

        trigger = self._dip_change_trigger()

        other = self._dip_dict_type.validated_dict(other)

        if trigger is not None:
            old = {}
            new = {}

            for key, value in other.items():
                try:
                    old_value = self[key]

                    if value != old_value:
                        old[key] = old_value
                        new[key] = value
                except KeyError:
                    new[key] = value

        super().update(other)

        if trigger is not None:
            self._dip_changed(trigger, new, old)

    def __setitem__(self, key, value):
        """ Reimplemented to validate the value. """

        trigger = self._dip_change_trigger()

        key = self._dip_dict_type.validate_collection_value(self._dip_key_type,
                key)
        value = self._dip_dict_type.validate_collection_value(
                self._dip_value_type, value)

        if trigger is not None:
            try:
                old = {key: self[key]}
            except KeyError:
                old = {}

            new = {key: value}

        super().__setitem__(key, value)

        if trigger is not None:
            self._dip_changed(trigger, new, old)

    def __delitem__(self, key):
        """ Reimplemented to trigger the change notification. """

        trigger = self._dip_change_trigger()

        key = self._dip_dict_type.validate_collection_value(self._dip_key_type,
                key)

        if trigger is not None:
            try:
                old = {key: self[key]}
            except KeyError:
                old = {}

        super().__delitem__(key)

        if trigger is not None:
            self._dip_changed(trigger, {}, old)
