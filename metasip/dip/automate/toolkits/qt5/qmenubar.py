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
from PyQt5.QtWidgets import QMenuBar

from ....automate import AutomationError, IAutomatedActionTrigger
from ....model import adapt, Adapter


@adapt(QMenuBar, to=IAutomatedActionTrigger)
class QMenuBarIAutomatedActionTriggerAdapter(Adapter):
    """ The QMenuBarIAutomatedActionTriggerAdapter adapts a
    :class:`~PyQt5.QtWidgets.QMenuBar` to the
    :class:`~dip.shell.IAutomatedActionTrigger` interface.
    """

    def simulate_trigger(self, id, delay, action_id):
        """ Simulate the user triggering a menu bar action.

        :param id:
            is the (possibly scoped) identifier of the widget.
        :param delay:
            is the delay in milliseconds between simulated events.
        :param action_id:
            is the identifier of the action.
        """

        qmenubar = self.adaptee

        # Find the path of actions to the one we want.
        action_path = self._find_action(qmenubar, action_id)
        if action_path is None:
            raise AutomationError(id, 'trigger',
                    "unknown menu id '{0}'".format(action_id))

        if qmenubar.isNativeMenuBar():
            # Qt doesn't provide valid geometry for actions in a native menu
            # bar so we fall back to just triggering the action.  The only real
            # disadvantage is that you don't get to see the menus appearing and
            # disappearing.
            action_path[-1].trigger()
        else:
            # Open each menu in turn before finally clicking on the action to
            # be triggered.
            container = qmenubar
            for action in action_path:
                geom = container.actionGeometry(action)
                if not geom.isValid():
                    raise AutomationError(id, 'trigger',
                            "a sub-menu action does not have a valid geometry")

                # Click in the middle of the action.
                QTest.mouseClick(container, Qt.LeftButton, pos=geom.center(),
                        delay=delay)

                # Descend to the next sub-menu.
                container = action.menu()

    @classmethod
    def _find_action(cls, container, action_id, action_path=None):
        """ Find an action and return the path of actions to get to it. """

        if action_path is None:
            action_path = []

        # Search this container's actions.
        for action in container.actions():
            # Assume we want to follow this path.
            new_action_path = list(action_path)
            new_action_path.append(action)

            if action.objectName() == action_id:
                return new_action_path

            menu = action.menu()
            if menu is not None:
                # Look in the sub-menu.
                new_action_path = cls._find_action(menu, action_id,
                        new_action_path)

                if new_action_path is not None:
                    return new_action_path

        return None
