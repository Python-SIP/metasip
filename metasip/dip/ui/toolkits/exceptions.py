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


class ToolkitError(Exception):
    """ The ToolkitError class is an exception raised when there is an error
    related to a particular toolkit.
    """

    def __init__(self, toolkit, error):
        """ Initialise the exception.

        :param toolkit:
            is the name of the toolkit.  It is available as the *toolkit*
            attribute.
        :param error:
            is a string describing the error.  It is available as the *error*
            attribute.
        """

        super().__init__()

        self.toolkit = toolkit
        self.error = error

    def __str__(self):
        """ Reimplemented to return a user friendly representation. """

        return "{0}: {1}".format(self.toolkit, self.error)
