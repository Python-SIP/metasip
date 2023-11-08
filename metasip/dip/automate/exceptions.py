# Copyright (c) 2011 Riverbank Computing Limited.
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


class AutomationError(Exception):
    """ The AutomationError exception is raised when an automated command
    cannot be executed.
    """

    def __init__(self, id, command, message):
        """ Initialise the exception.

        :param id:
            is the identifier of the item that the command was applied to.
        :param command:
            is the name of the command.
        :param message:
            the message describing the detail of the exception.
        """

        super().__init__(
                "'{0}' '{1}' command: {2}".format(id, command, message))
