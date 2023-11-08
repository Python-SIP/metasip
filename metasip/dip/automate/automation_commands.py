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


from ..model import Any, Int, Model


class AutomationCommands(Model):
    """ The AutomationCommands class is the base class for recording a sequence
    of commands to automate part of an application.
    """

    # The sequence number that defines the order in which this instance was
    # created relative to other instances.  This is used to ensure that
    # automation commands defined in the same .py file are applied in the order
    # that they are created in the file.
    sequence = Int()

    # An optional value that can be passed to __init__ and used by record().
    value = Any()

    def __init__(self, value=None):
        """ Initialise the object. """

        # It's more natural to pass this as a positional argument.
        self.value = value

    def record(self, robot):
        """ Record a sequence of automation commands for a user interface using
        a robot.

        :param robot:
            is the :class:`~dip.automate.Robot` to use to record the commands.
        """

        # This must be implemented by a sub-class.
        raise NotImplementedError
