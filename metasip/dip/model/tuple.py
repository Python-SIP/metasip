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
from .collection_type_factory import CollectionTypeFactory
from .exceptions import ValidationTypeError


# A unique object that is used to determine whether an optional argument was
# given or not.
DefaultArgValue = object()


class Tuple(CollectionTypeFactory):
    """ The Tuple class encapsulates a Python tuple with elements of a
    particular type.
    """

    def __init__(self, element_type=None, default=DefaultArgValue, allow_none=False, allow_rebind=True, getter=None, setter=None, **metadata):
        """ Initialise the object.

        :param element_type:
            the type of each element of the tuple.  If it is omitted then
            elements of any type are allowed.  If it is a string then it is
            the "full" name of the type.  The string form allows types to be
            specified while avoiding circular imports.
        :param default:
            is the default value of the tuple.  If is it omitted then an empty
            tuple is the default.
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
            default = ()

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
        """ Validate a tuple according to the constraints.  An exception is
        raised if the tuple is invalid.

        :param value:
            the tuple to validate.
        :return:
            the validated tuple.
        """

        if self.validate_none(value):
            return value

        # Make sure the type is resolved.
        self.element_type = self.resolve_type(self.element_type)

        # Allow any iterator.
        if not hasattr(value, '__iter__'):
            raise ValidationTypeError(type(self), tuple, value)

        return TupleImpl(self, self._validated_tuple(value))

    def _validated_tuple(self, value):
        """ Return a sequence containing validated elements.

        :param value:
            is the tuple of (possibly) invalid elements.
        :return:
            a corresponding sequence of validated elements.
        """

        # There is no need to validate an untyped tuple.
        if self.untyped(self.element_type):
            return value

        # We only need to check the type of a validated tuple.
        if isinstance(value, TupleImpl):
            if not self.untyped(value._dip_element_type):
                self.validate_collection_type(self.element_type,
                        value._dip_element_type)

                return value

        return [self.validate_collection_value(self.element_type, v)
                for v in value]


class TupleImpl(tuple):
    """ The TupleImpl class is a tuple that knows what type of element it
    contains.
    """

    def __new__(cls, tuple_type, validated_elements):
        """ Create the object.  We have to reimplement this because
        tuple.__new__() doesn't call __init__().
        """

        instance = tuple.__new__(cls, validated_elements)

        instance._dip_element_type = tuple_type.element_type

        return instance
