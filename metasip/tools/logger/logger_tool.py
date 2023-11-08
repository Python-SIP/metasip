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


from PyQt5.QtWidgets import QAbstractSlider, QApplication, QPlainTextEdit

from ...dip.model import unadapted
from ...dip.shell import SimpleViewTool

from ... import Logger


class LoggerTool(SimpleViewTool):
    """ The LoggerTool implements a tool for displaying the log. """

    # The action's identifier.
    action_id = 'metasip.actions.log'

    # The default area for the tool's view.
    area = 'dip.shell.areas.bottom'

    # The tool's identifier.
    id = 'metasip.tools.logger'

    # The tool's name.
    name = "Log"

    # The collection of actions that the tool's action will be placed in.
    within = 'dip.ui.collections.view'

    @SimpleViewTool.view.default
    def view(self):
        """ Invoked to create the tool's view. """

        # This instance is the logger.
        Logger().instance = self

        # Create the view.
        return QPlainTextEdit(readOnly=True)

    def log(self, message):
        """ Write a message to the log window.
    
        :param message:
            is the text of the message and should not include explicit
            newlines.
        """

        qview = unadapted(self.view)

        # Add the new message
        qview.appendPlainText(message)

        # Make sure the new message is visible.
        qview.verticalScrollBar().triggerAction(
                QAbstractSlider.SliderToMaximum)

        # Update the screen so that individual messages appear as soon as they
        # are logged.
        QApplication.processEvents()
