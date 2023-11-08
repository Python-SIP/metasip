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


from PyQt5.QtCore import Qt
from PyQt5.QtTest import QTest
from PyQt5.QtWidgets import QMenu

from ....automate import AutomationError, IAutomatedActionTrigger
from ....model import adapt, Adapter


@adapt(QMenu, to=IAutomatedActionTrigger)
class QMenuIAutomatedActionTriggerAdapter(Adapter):
    """ The QMenuIAutomatedActionTriggerAdapter adapts a
    :class:`~PyQt5.QtWidgets.QMenu` to the
    :class:`~dip.shell.IAutomatedActionTrigger` interface.
    """

    def simulate_trigger(self, id, delay, action_id):
        """ Simulate the user triggering a menu action.

        :param id:
            is the (possibly scoped) identifier of the widget.
        :param delay:
            is the delay in milliseconds between simulated events.
        :param action_id:
            is the identifier of the action.
        """

        menu = self.adaptee

        # Find the visible menu item that contains the action.
        # FIXME: Re-use the code from the QMenuBar adapter.
        for action in menu.actions():
            if action.isVisible() and action.objectName() == action_id:
                break
        else:
            raise AutomationError(id, 'trigger',
                    "unknown menu id '{0}'".format(action_id))

        pos = menu.actionGeometry(action).center()

        QTest.mouseClick(menu, Qt.LeftButton, pos=pos, delay=delay)
