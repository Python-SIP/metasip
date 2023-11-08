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


class Set(MutableTypeFactory):
    """ The Set class encapsulates a Python set with elements of a particular
    type.
    """

    def __init__(self, element_type=None, default=DefaultArgValue, allow_none=False, allow_rebind=True, getter=None, setter=None, **metadata):
        """ Initialise the object.

        :param element_type:
            the type of each element of the set.  If it is omitted then
            elements of any type are allowed.  If it is a string then it is
            the "full" name of the type.  The string form allows types to be
            specified while avoiding circular imports.
        :param default:
            is the default value of the set.  If is it omitted then an empty
            set is the default.
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
            default = set()

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
        """ Validate a set according to the constraints.  An exception is
        raised if the set is invalid.

        :param value:
            the set to validate.
        :return:
            the validated set.
        """

        if self.validate_none(value):
            return value

        # Make sure the type is resolved.
        self.element_type = self.resolve_type(self.element_type)

        if not isinstance(value, set):
            raise ValidationTypeError(type(self), set, value)

        return SetImpl(self, self.validated_set(value))

    def validated_set(self, value):
        """ Return a set containing validated elements.

        :param value:
            the set of (possibly) invalid elements.
        :return:
            a corresponding set of validated elements.
        """

        # There is no need to validate an untyped set.
        if self.untyped(self.element_type):
            return value

        # We only need to check the type of a validated set.
        if isinstance(value, SetImpl):
            if not self.untyped(value._dip_element_type):
                self.validate_collection_type(self.element_type,
                        value._dip_element_type)

                return value

        return {self.validate_collection_value(self.element_type, v)
                for v in value}


class SetImpl(set):
    """ The SetImpl class is a set that validates new elements against a type.
    """

    def __init__(self, set_type, validated_set):
        """ Initialise the object. """

        self._dip_set_type = set_type
        self._dip_element_type = set_type.element_type
        self._dip_model = None

        super().__init__(validated_set)

    def _dip_changed(self, trigger, new, old):
        """ Notify any change. """

        if new != old:
            trigger.change = AttributeChange(model=self._dip_model,
                    name=self._dip_set_type.name, new=new, old=old)

    def _dip_change_trigger(self):
        """ Return the change trigger if there is one. """

        model = self._dip_model

        return None if model is None else get_change_trigger(model,
                self._dip_set_type.name)

    def add(self, element):
        """ Reimplemented to validate the new element. """

        trigger = self._dip_change_trigger()

        element = self._dip_set_type.validate_collection_value(
                self._dip_element_type, element)

        old_size = len(self)

        super().add(element)

        if trigger is not None and old_size != len(self):
            self._dip_changed(trigger, set([element]), set())

    def clear(self):
        """ Reimplemented to trigger the change notification. """

        trigger = self._dip_change_trigger()

        if trigger is not None:
            old = set(self)

        super().clear()

        if trigger is not None:
            self._dip_changed(trigger, set(), old)

    def difference_update(self, *others):
        """ Reimplemented to trigger the change notification. """

        trigger = self._dip_change_trigger()

        if trigger is not None:
            orig = set(self)

        others = [self._dip_set_type.validated_set(other) for other in others]

        super().difference_update(*others)

        if trigger is not None:
            self._dip_changed(trigger, set(), orig - self)

    def __isub__(self, other):
        """ Reimplemented to trigger the change notification. """

        trigger = self._dip_change_trigger()

        if trigger is not None:
            orig = set(self)

        other = self._dip_set_type.validated_set(other)

        ret = super().__isub__(other)

        if trigger is not None:
            self._dip_changed(trigger, set(), orig - ret)

        return ret

    def discard(self, element):
        """ Reimplemented to trigger the change notification. """

        trigger = self._dip_change_trigger()

        element = self._dip_set_type.validate_collection_value(
                self._dip_element_type, element)

        old_size = len(self)

        super().discard(element)

        if trigger is not None and old_size != len(self):
            self._dip_changed(trigger, set(), set([element]))

    def intersection_update(self, *others):
        """ Reimplemented to trigger the change notification. """

        trigger = self._dip_change_trigger()

        if trigger is not None:
            orig = set(self)

        others = [self._dip_set_type.validated_set(other) for other in others]

        super().intersection_update(*others)

        if trigger is not None:
            self._dip_changed(trigger, set(), orig - self)

    def __iand__(self, other):
        """ Reimplemented to trigger the change notification. """

        trigger = self._dip_change_trigger()

        if trigger is not None:
            orig = set(self)

        other = self._dip_set_type.validated_set(other)

        ret = super().__iand__(other)

        if trigger is not None:
            self._dip_changed(trigger, set(), orig - ret)

        return ret

    def pop(self):
        """ Reimplemented to trigger the change notification. """

        trigger = self._dip_change_trigger()

        element = super().pop()

        if trigger is not None:
            self._dip_changed(trigger, set(), set([element]))

        return element

    def remove(self, element):
        """ Reimplemented to trigger the change notification. """

        trigger = self._dip_change_trigger()

        element = self._dip_set_type.validate_collection_value(
                self._dip_element_type, element)

        super().remove(element)

        if trigger is not None:
            self._dip_changed(trigger, set(), set([element]))

    def symmetric_difference_update(self, other):
        """ Reimplemented to trigger the change notification. """

        trigger = self._dip_change_trigger()

        if trigger is not None:
            orig = set(self)

        other = self._dip_set_type.validated_set(other)

        super().symmetric_difference_update(other)

        if trigger is not None:
            self._dip_changed(trigger, self - orig, orig - self)

    def __ixor__(self, other):
        """ Reimplemented to trigger the change notification. """

        trigger = self._dip_change_trigger()

        if trigger is not None:
            orig = set(self)

        other = self._dip_set_type.validated_set(other)

        ret = super().__ixor__(other)

        if trigger is not None:
            self._dip_changed(trigger, ret - orig, orig - ret)

        return ret

    def update(self, *others):
        """ Reimplemented to trigger the change notification. """

        trigger = self._dip_change_trigger()

        if trigger is not None:
            orig = set(self)

        others = [self._dip_set_type.validated_set(other) for other in others]

        super().update(*others)

        if trigger is not None:
            self._dip_changed(trigger, self - orig, set())

    def __ior__(self, other):
        """ Reimplemented to trigger the change notification. """

        trigger = self._dip_change_trigger()

        if trigger is not None:
            orig = set(self)

        other = self._dip_set_type.validated_set(other)

        ret = super().__ior__(other)

        if trigger is not None:
            self._dip_changed(trigger, ret - orig, set())

        return ret
