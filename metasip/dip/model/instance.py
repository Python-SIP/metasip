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
from .exceptions import ValidationError


class Instance(CollectionTypeFactory):
    """ The Instance class encapsulates an instance of a number of types. """

    def __init__(self, *types, default=None, allow_none=True, allow_rebind=True, getter=None, setter=None, **metadata):
        """ Initialise the object.

        :param types:
            the allowable types of the instance.  If no types are specified
            then an instance of any type is allowed.  If any type is a string
            then it is the "full" name of the type.  The string form allows
            types to be specified while avoiding circular imports.
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
        :param metadata:
            is additional meta-data stored with the type.
        """

        self.types = types
        self._resolved = None

        super().__init__(default, allow_none, allow_rebind, getter, setter,
                metadata)

    def copy(self):
        """ Create a copy of this instance.

        :return:
            the copied instance.
        """

        return self.__class__(*self.types, default=self.default_value,
                allow_none=self.allow_none, allow_rebind=self.allow_rebind,
                getter=self.getter_func, setter=self.setter_func,
                **self.metadata)

    def validate(self, value):
        """ Validate an instance according to the constraints.  An exception
        is raised if the instance is invalid.

        :param value:
            the instance to validate.
        :return:
            the validated instance.
        """

        if self.validate_none(value):
            return value

        if self._resolved is None:
            self.types = self._resolved = [
                    self.resolve_type(t, "instance", allow_none=False)
                    for t in self.types]

        last_exception = None

        for instance_type in self._resolved:
            try:
                validated = self.validate_collection_value(instance_type, value)
            except ValidationError as e:
                last_exception = e
            else:
                last_exception = None
                break
        else:
            validated = value

        if last_exception is None:
            return validated

        # If there was only one possible type then re-raise the exception.
        if len(self.types) == 1:
            raise last_exception

        # Raise a more generic exception if there were a number of possible
        # types.
        raise ValidationError(*self.types,
                message="validation failed for all types")

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
