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


from .collection_type_factory import CollectionTypeFactory
from .exceptions import ValidationTypeError


class Subclass(CollectionTypeFactory):
    """ The Subclass class encapsulates any type object. """

    def __init__(self, type, default=None, allow_none=True, allow_rebind=True, getter=None, setter=None, **metadata):
        """ Initialise the object.

        :param type:
            is the type object.
        :param default:
            the default attribute value.  If omitted then ``None`` is used.
        :param allow_none:
            ``True`` if ``None`` is a valid value.  The default is ``True``.
        :param allow_rebind:
            ``True`` if the attribute can be re-bound after the model has been
            instantiated.
        :param getter:
            is the optional attribute getter.
        :param setter:
            is the optional attribute setter.
        :param \*\*metadata:
            is additional meta-data stored with the type.
        """

        self.type = type

        super().__init__(default, allow_none, allow_rebind, getter, setter,
                metadata)

    def copy(self):
        """ Create a copy of this instance.

        :return:
            the copied instance.
        """

        return self.__class__(self.type, self.default_value, self.allow_none,
                self.allow_rebind, self.getter_func, self.setter_func,
                **self.metadata)

    def validate(self, value):
        """ Validate an object according to the constraints.  An exception is
        raised if the object is invalid.

        :param value:
            the object to validate.
        :return:
            the validated object.
        """

        if self.validate_none(value):
            return value

        self.type = self.resolve_type(self.type, "subclass", allow_none=False)

        try:
            valid = issubclass(value, self.type)
        except TypeError:
            valid = False

        if not valid:
            raise ValidationTypeError(type(self), self.type, value)

        return value

    @classmethod
    def different(cls, value1, value2):
        """ Reimplemented to compare two sub-classes to see if they are
        different.

        :param value1:
            is the first value.
        :param value2:
            is the second value.
        :return:
            ``True`` if the values are different.
        """

        return value1 is not value2
