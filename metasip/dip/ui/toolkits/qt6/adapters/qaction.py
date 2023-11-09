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


from PyQt6.QtGui import QAction

from .....model import adapt, notify_observers
from .....ui import IAction

from .object_adapter import ObjectAdapter


@adapt(QAction, to=IAction)
class QActionIActionAdapter(ObjectAdapter):
    """ An adapter to implement IAction for a QAction. """

    def configure(self, properties):
        """ Configure the action. """

        self.adaptee.triggered[bool].connect(self.__on_triggered)

        super().configure(properties)

    @IAction.checkable.getter
    def checkable(self):
        """ The getter for the action's checkable state. """

        return self.adaptee.isCheckable()

    @checkable.setter
    def checkable(self, value):
        """ The setter for the action's checkable state. """

        self.adaptee.setCheckable(value)

    @IAction.checked.getter
    def checked(self):
        """ The getter for the action's checked state. """

        return self.adaptee.isChecked()

    @checked.setter
    def checked(self, value):
        """ The setter for the action's checked state. """

        self.adaptee.setChecked(value)

    @IAction.enabled.getter
    def enabled(self):
        """ The getter for the action's enabled state. """

        return self.adaptee.isEnabled()

    @enabled.setter
    def enabled(self, value):
        """ The setter for the action's enabled state. """

        self.adaptee.setEnabled(value)

    @IAction.plain_text.getter
    def plain_text(self):
        """ The getter for the action's plain text. """

        return self.adaptee.text().replace('&', '').replace('...', '')

    @IAction.shortcut.getter
    def shortcut(self):
        """ The getter for the action's shortcut. """

        return self.adaptee.shortcut().toString()

    @shortcut.setter
    def shortcut(self, value):
        """ The setter for the action's shortcut. """

        self.adaptee.setShortcut(value)

    @IAction.status_tip.getter
    def status_tip(self):
        """ The getter for the action's status tip. """

        return self.adaptee.statusTip()

    @status_tip.setter
    def status_tip(self, value):
        """ The setter for the action's status tip. """

        self.adaptee.setStatusTip(value)

    @IAction.text.getter
    def text(self):
        """ The getter for the action's text. """

        return self.adaptee.text()

    @text.setter
    def text(self, value):
        """ The setter for the action's text. """

        self.adaptee.setText(value)

    @IAction.tool_tip.getter
    def tool_tip(self):
        """ The getter for the action's tool tip. """

        return self.adaptee.toolTip()

    @tool_tip.setter
    def tool_tip(self, value):
        """ The setter for the action's tool tip. """

        self.adaptee.setToolTip(value)

    @IAction.visible.getter
    def visible(self):
        """ The getter for the action's visible state. """

        return self.adaptee.isVisible()

    @visible.setter
    def visible(self, value):
        """ The setter for the action's visible state. """

        self.adaptee.setVisible(value)

    @IAction.whats_this.getter
    def whats_this(self):
        """ The getter for the action's "Whats This?" help. """

        return self.adaptee.whatsThis()

    @whats_this.setter
    def whats_this(self, value):
        """ The setter for the action's "Whats This?" help. """

        self.adaptee.setWhatsThis(value)

    def __on_triggered(self, checked):
        """ Invoked when the action is triggered. """

        if self.when_triggered is not None:
            self.when_triggered(self)

        self.trigger = True

        if self.adaptee.isCheckable():
            notify_observers('checked', self, checked, not checked)
