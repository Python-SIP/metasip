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


from PyQt4.QtGui import QMenuBar

from .....model import adapt, unadapted
from .....ui import IAction, IActionCollection, IMenu, IMenuBar

from .place_holder import PlaceHolder
from .view_adapters import ViewWidgetAdapter


@adapt(QMenuBar, to=IMenuBar)
class QMenuBarIMenuBarAdapter(ViewWidgetAdapter):
    """ The QMenuBarIMenuBarAdapter adapts a :class:`~PyQt4.QtGui.QMenuBar` to
    the :class:`~dip.pui.IMenuBar` interface.
    """

    @IMenuBar.views.getter
    def views(self):
        """ Invoked to get the views. """

        return tuple(IMenu(action.menu()) for action in self.adaptee.actions())

    @views.setter
    def views(self, value):
        """ Invoked to set the views. """

        qmenubar = self.adaptee

        qmenubar.clear()

        for menu in value:
            qmenubar.addMenu(unadapted(menu))

    def add_action(self, action):
        """ Try and add an action or action collection to the menu bar.

        :param action:
            is the action.
        :return:
            ``True`` if the action was added.  ``False`` is returned if the
            menu bar couldn't accommodate the action's desired positioning.
        """

        if isinstance(action, IActionCollection):
            action_collection = action

            if PlaceHolder.add_action_collection(action_collection, self.adaptee):
                return True

            if action_collection.within != '':
                return False

            qaction = PlaceHolder.as_QMenu(action_collection, self.adaptee).menuAction()
        else:
            if PlaceHolder.add_action(action, self.adaptee):
                return True

            # The action might be a QAction.
            if IAction(action).within != '':
                return False

            qaction = PlaceHolder.as_QAction(action, self.adaptee)

        # We put the new action immediately before the Help menu.
        for qact in self.adaptee.actions():
            qmenu = qact.menu()
            if qmenu is None:
                continue

            if qmenu.objectName() == 'dip.ui.collections.help':
                self.adaptee.insertAction(qact, qaction)
                break
        else:
            self.adaptee.addAction(qaction)

        return True
