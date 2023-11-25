# Copyright (c) 2023 Riverbank Computing Limited.
#
# This file is part of metasip.
#
# This file may be used under the terms of the GNU General Public License v3
# as published by the Free Software Foundation which can be found in the file
# LICENSE-GPL3.txt included in this package.
#
# This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
# WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.


from PyQt6.QtWidgets import QAbstractSlider, QApplication, QPlainTextEdit

from ..shell import EventType
from ..shell_tool import ShellTool, ShellToolLocation


class LoggerTool(ShellTool):
    """ This class implements a tool for displaying the log. """

    def __init__(self, shell):
        """ Initialise the tool. """

        super().__init__(shell)

        self._log_widget = QPlainTextEdit(readOnly=True)

    def event(self, event_type, event_arg):
        """ Reimplemented to handle project-specific events. """

        if event_type is EventType.LOG_MESSAGE:
            self._log_message(event_arg)

    @property
    def location(self):
        """ Get the location of the tool in the shell. """

        return ShellToolLocation.BOTTOM

    @property
    def name(self):
        """ Get the tool's name. """

        return 'metasip.tool.logger'

    @property
    def title(self):
        """ Get the tool's title. """

        return "Log"

    @property
    def widget(self):
        """ Get the tool's widget. """

        return self._log_widget

    def _log_message(self, message):
        """ Log a message. """

        # Add the new message
        self._log_widget.appendPlainText(message)

        # Make sure the new message is visible.
        self._log_widget.verticalScrollBar().triggerAction(
                QAbstractSlider.SliderAction.SliderToMaximum)

        # Update the screen so that individual messages appear as soon as they
        # are logged.
        QApplication.processEvents()
