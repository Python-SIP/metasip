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


from .exceptions import ValidationError, ValidationTypeError
from .value_type_factory import ValueTypeFactory


class Enum(ValueTypeFactory):
    """ The Enum class encapsulates a fixed set of string values. """

    def __init__(self, *members, default=None, allow_none=False, allow_rebind=True, getter=None, setter=None, **metadata):
        """ Initialise the object.

        :param \*members:
            the list of members.
        :param default:
            the default attribute value.  If omitted then the first member is
            used.
        :param allow_none:
            ``True`` if ``None`` is a valid value.  The default is ``False``.
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

        if len(members) == 0:
            raise ValidationError(type(self), message="no members defined")

        for member in members:
            if not isinstance(member, str):
                raise ValidationTypeError(type(self), str, member)

        self.members = members

        if default is None and not allow_none:
            default = members[0]

        super().__init__(default, allow_none, allow_rebind, getter, setter,
                metadata)

    def copy(self):
        """ Create a copy of this instance.

        :return:
            the copied instance.
        """

        return self.__class__(*self.members, default=self.default_value,
                allow_none=self.allow_none, allow_rebind=self.allow_rebind,
                getter=self.getter_func, setter=self.setter_func,
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

        if value not in self.members:
            member_list = ', '.join(
                    ['\'' + member + '\'' for member in self.members])

            raise ValidationError(type(self),
                    message="expected one of {0}, not '{1}'".format(
                            member_list, value))

        return value
