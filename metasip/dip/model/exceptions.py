# Copyright (c) 2009 Riverbank Computing Limited.
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


class ValidationError(TypeError):
    """ The ValidationError exception is raised when a value is invalid. """

    def __init__(self, *types, message):
        """ Initialise the exception.

        :param types:
            the types that attempted to validate the value.
        :param message:
            the text of the message describing the detail of the error.
        """

        type_names = ', '.join([type.__name__ for type in types])

        super().__init__(
                "{0} validation error: {1}".format(type_names, message))


class ValidationTypeError(ValidationError):
    """ The ValidationTypeError exception is raised when a value has an
    invalid type.
    """

    def __init__(self, model_type, py_type, value):
        """ Initialise the exception.

        :param model_type:
            the model type that validated the value.
        :param py_type:
            the Python type that the value was expected to be.
        :param value:
            the value that was invalid.
        """

        super().__init__(model_type,
                message="a type '{0}' was expected, not type '{1}'".format(
                        py_type.__name__, type(value).__name__))
