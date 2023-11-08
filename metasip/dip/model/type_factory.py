# Copyright (c) 2010 Riverbank Computing Limited.
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



class TypeFactory:
    """ The TypeFactory class is the base class for all classes that create
    attribute types.
    """

    def __init__(self, metadata):
        """ Initialise the object.

        :param metadata:
            is a dictionary of additional meta-data stored with the type.
        """

        super().__init__()

        self.metadata = metadata

        # These will get set by the meta-type when the scoping class is
        # created.
        self.name = None
        self.model_type = None

        self._observed_func = None

    def clone(self):
        """ Create a clone of this instance.

        :return:
            the cloned instance.
        """

        clone = self.copy()
        clone.name = self.name
        clone.model_type = self.model_type
        clone._observed_func = self._observed_func

        return clone

    def copy(self):
        """ Create a copy of this instance.

        :return:
            the copied instance.
        """

        return self.__class__(**self.metadata)

    def observed(self, observed_func):
        """ This is used to decorate a method that will be invoked when the
        number of observers that a typed attribute has changes.  The name of
        the method should be the same as the name of the attribute.
        """

        clone = self.clone()
        clone._observed_func = observed_func

        return clone

    def __get__(self, instance, owner):
        """ Raise an exception as there is no value to get. """

        if instance is None:
            return self

        raise AttributeError(
                "'{0}' attributes cannot be read".format(type(self).__name__))

    def __set__(self, instance, value):
        """ This must be reimplemented by a sub-class. """

        raise NotImplementedError

    def __delete__(self, instance):
        """ Raise an exception as attributes cannot be deleted. """

        raise AttributeError(
                "'{0}' attributes cannot be deleted".format(
                        type(self).__name__))
