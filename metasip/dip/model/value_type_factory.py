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


from .change_trigger import get_change_trigger
from .exceptions import ValidationError
from .type_factory import TypeFactory


class ValueTypeFactory(TypeFactory):
    """ The ValueTypeFactory class is the base class for all classes that
    create attribute types that have an associated stored value.
    """

    def __init__(self, default, allow_none, allow_rebind, getter, setter, metadata):
        """ Initialise the object.

        :param default:
            is the default value of the type.
        :param allow_none:
            ``True`` if ``None`` is a valid value.
        :param allow_rebind:
            ``True`` if the attribute can be re-bound after the model has been
            instantiated.
        :param getter:
            is the optional attribute getter.
        :param setter:
            is the optional attribute setter.
        :param metadata:
            is a dictionary of additional meta-data stored with the type.
        """

        super().__init__(metadata)

        self.allow_none = allow_none
        self.allow_rebind = allow_rebind
        self.getter_func = getter
        self.setter_func = setter
        self._default_func = None

        self.set_default_value(default)

    def bind(self, model, value, rebind=False):
        """ This is called when a model attribute is being bound or rebound.

        :param model:
            is the model.
        :param value:
            is the attribute's new value.
        :param rebind:
            is set if the attribute already has a value.
        """

        # This default implementation does nothing.
        pass

    def clone(self):
        """ Create a clone of this instance.

        :return:
            the cloned instance.
        """

        clone = super().clone()
        clone._default_func = self._default_func

        return clone

    def copy(self):
        """ Create a copy of this instance.  This implementation is suitable
        for types that don't have any additional data.

        :return:
            the copied instance.
        """

        return self.__class__(self.default_value, self.allow_none,
                self.allow_rebind, self.getter_func, self.setter_func,
                **self.metadata)

    def get_default_value(self):
        """ Get the type's default value.  This implementation is appropriate
        for immutable types.  Mutable types should ensure a copy of the default
        is returned.

        :return:
            the default value.
        """

        # The default value is validated here (i.e. relatively late) so that
        # there is enough information for type names to be resolved.
        return self.validate(self.default_value)

    def set_default_value(self, default):
        """ Set the type's default value.

        :param default:
            is the new default value.
        """

        self.default_value = default

    def __call__(self, getter_func):
        """ This is used to implicitly define a typed attribute by decorating
        the getter method.  The name of the method is used as the name of the
        attribute.
        """

        self.name = getter_func.__name__

        return self.getter(getter_func)

    def validate(self, value):
        """ Validate a value according to the type's constraints.  An
        exception is raised if the value is invalid.

        :param value:
            the value to validate.
        :return:
            the validated value (which may be normalised in some way).
        """

        self.validate_none(value)

        return value

    def validate_none(self, value):
        """ Validate a possibly ``None`` value.

        :param value:
            the value to validate.
        :return:
            ``True`` if the value is ``None`` and is valid.  ``False`` is
            returned if the value is not ``None``.  An exception is raised if
            the value is ``None`` but this is invalid.
        """

        if value is None:
            if self.allow_none:
                return True

            raise ValidationError(type(self), message="value must not be None")

        return False

    def default(self, default_func):
        """ This is used to decorate a method that will be invoked to provide
        the default value of a typed attribute.  The name of the method should
        be the same as the name of the attribute.
        """

        clone = self.clone()
        clone._default_func = default_func

        return clone

    def getter(self, getter_func):
        """ This is used to decorate a method that will be invoked to get the
        value of a typed attribute.  The name of the method should be the same
        as the name of the attribute.
        """

        clone = self.clone()
        clone.getter_func = getter_func

        return clone

    def setter(self, setter_func):
        """ This is used to decorate a method that will be invoked to set the
        value of a typed attribute.  The name of the method should be the same
        as the name of the attribute.
        """

        clone = self.clone()
        clone.setter_func = setter_func

        return clone

    def __get__(self, instance, owner):
        """ Reimplemented to get the real value from the instance. """

        if instance is None:
            return self

        # See if this is the first time the value has been referenced.
        shadow = '_' + self.name
        value = getattr(instance, shadow)

        if value is Uninitialized:
            # We know there is a default function.
            getter_func = self._default_func
        else:
            # Invoke an explicit getter if there is one.
            getter_func = self.getter_func

        if getter_func is not None:
            value = self.validate(getter_func(instance))
            self.bind(instance, value)
            setattr(instance, shadow, value)

        return value

    def __set__(self, instance, value):
        """ Reimplemented to validate the value before setting it and to
        trigger any changes.
        """

        if not self.allow_rebind:
            raise AttributeError(
                    "'{0}' can only be set when the object is created".format(
                            self.name))

        self.set_value(instance, self.name, value)

    def set_value(self, instance, name, value):
        """ Set the value of an attribute.

        :param instance:
            is the instance of the model.
        :param name:
            is the name of the attribute.
        :param value:
            is the value to set.
        """

        value = self.validate(value)
        self.bind(instance, value, rebind=True)

        # Save the old value if the attribute is being observed.
        trigger = get_change_trigger(instance, name)

        if trigger is not None:
            old = getattr(instance, name)

        setter_func = self.setter_func

        if setter_func is not None:
            setter_func(instance, value)

        # Save the new value in the shadow attribute, even if there is an
        # explicit setter.
        shadow = '_' + self.name
        setattr(instance, shadow, value)

        # See if the value has really changed.
        if trigger is not None and self.different(old, value):
            # Avoid a circular import.
            from .attribute_change import AttributeChange

            trigger.change = AttributeChange(model=instance, name=name,
                    new=value, old=old)

    @classmethod
    def different(cls, value1, value2):
        """ Compare two valid values to see if they are different.

        :param value1:
            is the first value.
        :param value2:
            is the second value.
        :return:
            ``True`` if the values are different.
        """

        return value1 != value2


# A unique object that it a placeholder for an uninitialized attribute.
Uninitialized = object()
