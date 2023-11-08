# Copyright (c) 2023 Riverbank Computing Limited.
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


import sys

from .any import Any
from .exceptions import ValidationError, ValidationTypeError
from .meta_interface import MetaInterface
from .value_type_factory import ValueTypeFactory


class CollectionTypeFactory(ValueTypeFactory):
    """ The CollectionTypeFactory class is a base class for all types that
    encapsulate objects of a particular type.
    """

    @classmethod
    def validate_collection_value(cls, collection_type, value):
        """ Validate a value contained in a collection.  An exception is raised
        if the value is invalid.

        :param collection_type:
            is the Python type or :class:`~dip.model.ValueTypeFactory`
            sub-class that is the value is expected to be.
        :param value:
            is the value to validate.
        :return:
            the validated value.
        """

        if cls.untyped(collection_type):
            return value

        # If it is an interface then see if the value can be adapted.
        if isinstance(collection_type, MetaInterface):
            adapted = collection_type(value, exception=False)
            if adapted is not None:
                return adapted

        # If it is a Python type then just check the value is an instance of
        # it.
        if isinstance(collection_type, type):
            if isinstance(value, collection_type):
                return value

            raise ValidationTypeError(cls, collection_type, value)

        # Ask the type to validate it.
        return collection_type.validate(value)

    @classmethod
    def validate_collection_type(cls, collection_type, other, context="element"):
        """ Validate a type (either an instance of the builtin ``type`` or an
        instance of an attribute type factory) against a type associated with a
        collection.  An exception is raised if the types are not compatible.

        :param collection_type:
            is the type associated with the collection.
        :param other:
            is the type to validate.
        :param context:
            is the context in which the type is used and is only used in the
            text of exceptions.
        """

        if isinstance(collection_type, type):
            if issubclass(other, collection_type):
                return
        elif issubclass(type(other), type(collection_type)):
            return

        # Get the types to get useful names for the exception.
        if not isinstance(collection_type, type):
            collection_type = type(collection_type)

        if not isinstance(other, type):
            other = type(other)

        raise ValidationError(cls,
                message="{0} type '{1}' was expected, not type '{2}'".format(
                        context, collection_type.__name__, other.__name__))

    def resolve_type(self, type_specification, context="element", allow_none=True):
        """ Resolve a type specification which is either ``None``, a Python
        type (i.e. an instance of ``type``), an instance of
        :class:`~dip.model.ValueTypeFactory` or a string that is the absolute
        or relative name of a Python type.  The string form allows types to be
        specified while avoiding circular imports.

        :param type_specification:
            the type specification to resolve.
        :param context:
            is the context in which the type is used and is only used in the
            text of exceptions.
        :param allow_none:
            is ``True`` if the type specification can be ``None``.
        :return:
            the resolved type.
        """

        # If it is None then there is nothing to do.
        if type_specification is None and allow_none:
            return None

        # If it is a ValueTypeFactory instance then propagate the model type.
        if isinstance(type_specification, ValueTypeFactory):
            type_specification.model_type = self.model_type
            return type_specification

        # If it is a Python type then there is nothing to do.
        if isinstance(type_specification, type):
            return type_specification

        # It must now be the name of a Python type.
        if not isinstance(type_specification, str):
            raise TypeError(
                    "{0} type error: a string, 'type' or 'ValueTypeFactory "
                    "instance was expected as the {1} type, not '{2}'".format(
                            type(self).__name__, context,
                            type(type_specification).__name__))

        parts = type_specification.split('.')

        if parts[0] == '':
            # Make a relative name absolute.
            dots = 0
            while dots < len(parts) and parts[dots] == '':
                dots += 1

            root_parts = self.model_type.__module__.split('.')

            if dots > len(root_parts):
                raise AttributeError("'{0}' has too many leading dots".format(
                        type_specification))

            parts = root_parts[:-dots] + parts[dots:]

        # A hack now that dip has been vendored into metasip.
        if parts[0] == 'dip':
            parts.insert(0, 'metasip')

        module_name = '.'.join(parts[:-1])
        type_name = parts[-1]

        try:
            __import__(module_name)
        except ImportError:
            raise AttributeError("no such module '{0}'".format(module_name))

        module = sys.modules[module_name]

        try:
            return getattr(module, type_name)
        except AttributeError:
            raise AttributeError(
                    "module '{0}' has no attribute '{1}'".format(
                            module_name, type_name))

    @staticmethod
    def untyped(collection_type):
        """ Return True if a type corresponds to an untyped collection. """

        return collection_type is None or isinstance(collection_type, Any)
