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


class StorageError(Exception):
    """ The StorageError class is an exception raised when there is an error
    accessing a particular storage location.
    """

    def __init__(self, error, location):
        """ Initialise the exception.

        :param error:
            is a string describing the error.  It is available as the *error*
            attribute.
        :param location:
            is a :class:`~dip.io.IStorageLocation` implementation where the
            error occurred.  It is available as the ``location`` attribute.
        """

        super().__init__()

        self.error = error
        self.location = location

    def __str__(self):
        """ Reimplemented to return a user friendly representation. """

        # Use a similar format to IOError.
        return "{0}: '{1}'".format(self.error, self.location)


class FormatError(StorageError):
    """ The FormatError class is an exception raised when there is an error
    decoding or encoding an object at a particular storage location.
    """
