# Copyright (c) 2017 Riverbank Computing Limited.
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


# FIXME: replace with proper toolkit support.
from .. import TOOLKIT
if TOOLKIT == 'qt4':
    from PyQt4.QtCore import QTimer
else:
    from PyQt5.QtCore import QTimer

from ..model import Int, List, Model

from .robot_command import RobotCommand


class Robot(Model):
    """ The Robot class manages the automation commands that can be executed by
    a user interface.
    """

    # The default delay in milliseconds between the playing of individual
    # automation commands.
    delay = Int(-1)

    # The default time in milliseconds to wait for a user interface widget to
    # be visible.
    timeout = Int(-1)

    # The list of commands that can be played.
    _commands = List(RobotCommand)

    def clear(self):
        """ Any recorded automation commands are discarded. """

        self._commands = []

    def play(self, after=-1):
        """ Any recorded automation commands are executed.

        :param after:
            is the delay in milliseconds after the start of an event loop
            before the commands are executed.  If the value is negative then
            the commands are played immediately without waiting for an event
            loop to start.
        """

        if after < 0:
            self._play_commands()
        else:
            QTimer.singleShot(after, self._play_commands)

    def _play_commands(self):
        """ Play the recorded commands. """

        for command in self._commands:
            command()

    def record(self, id, command, *command_args, delay=-1, timeout=-1, **command_kwargs):
        """ Record an automation command.

        :param id:
            is the (possibly scoped) identifier of the widget to apply the
            command to.
        :param command:
            is the name of the command to record.
        :param \*command_args:
            are the commands's positional arguments.
        :param delay:
            is the delay in milliseconds between simulated events.
        :param timeout:
            is the time in milliseconds to wait for the user interface widget
            to become visible.
        :param \*\*command_kwargs:
            are the commands's keyword arguments.
        """

        # Apply the defaults if needed.
        if delay < 0:
            delay = self.delay

        if timeout < 0:
            timeout = self.timeout

        command = RobotCommand(id=id, command=command,
                command_args=command_args, command_kwargs=command_kwargs,
                        delay=delay, timeout=timeout)
        self._commands.append(command)

    @staticmethod
    def simulate(id, command, *command_args, delay=-1, timeout=-1, **command_kwargs):
        """ Immediately execute an automation command.

        :param id:
            is the (possibly scoped) identifier of the widget to apply the
            command to.
        :param command:
            is the name of the command to execute.
        :param \*command_args:
            are the command's positional arguments.
        :param delay:
            is the delay in milliseconds between simulated events.
        :param timeout:
            is the time in milliseconds to wait for the user interface widget
            to become visible.
        :param \*\*command_kwargs:
            are the command's keyword arguments.
        """

        command = RobotCommand(id=id, command=command,
                command_args=command_args, command_kwargs=command_kwargs,
                delay=delay, timeout=timeout)
        command()
