# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


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
