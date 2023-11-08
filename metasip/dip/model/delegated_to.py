# Copyright (c) 2012 Riverbank Computing Limited.
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


from .value_type_factory import ValueTypeFactory


class DelegatedTo(ValueTypeFactory):
    """ The DelegatedTo class implements a delegate for another typed
    attribute.
    """

    def __init__(self, to, **metadata):
        """ Initialise the object.

        :param to:
            is the :term:`attribute path` of the attribute to delegate to.
        :param \*\*metadata:
            is additional meta-data stored with the type.
        """

        super().__init__(None, True, True, None, None, metadata)

        self._to = to.split('.')

    def delegates_to(self, instance):
        """ Get the containing model and name of the attribute that the
        delegate is acting for.

        :param instance:
            is the :class:`~dip.model.DelegatedTo` instance.
        :return:
            a tuple of the containing model and the name of the attribute.
        """

        for part in self._to[:-1]:
            instance = getattr(instance, part)

        return instance, self._to[-1]

    def copy(self):
        """ Create a copy of this instance.

        :return:
            the copied instance.
        """

        return self.__class__('.'.join(self._to), **self.metadata)

    def validate(self, value):
        """ Validate a value.  This is only called to validate the default
        value which is a dummy.

        :param value:
            the value to validate.
        :return:
            the validated value.
        """

        return value

    def __get__(self, instance, owner):
        """ Reimplemented to get the real value from the instance. """

        if instance is None:
            return self

        model, name = self.delegates_to(instance)

        return getattr(model, name)

    def __set__(self, instance, value):
        """ Reimplemented to validate the value before setting it. """

        model, name = self.delegates_to(instance)

        setattr(model, name, value)
