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


import sys

from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QMenu

from .....model import adapt, observe, unadapted
from .....ui import IAction, IActionCollection, IMenu

from .place_holder import PlaceHolder
from .view_adapters import ViewWidgetAdapter


@adapt(QMenu, to=IMenu)
class QMenuIMenuAdapter(ViewWidgetAdapter):
    """ The QMenuIMenuAdapter adapts a :class:`~PyQt6.QtWidgets.QMenu` to the
    :class:`~dip.pui.IMenu` interface.
    """

    def __init__(self):
        """ Initialise the adapter. """

        super().__init__()

        self._update_visibility(self._visible)

    @IMenu.title.getter
    def title(self):
        """ Invoked to get the menu's title. """

        return self.adaptee.title()

    @title.setter
    def title(self, value):
        """ Invoked to set the menu's title. """

        self.adaptee.setTitle(value)

    @IMenu.visible.getter
    def visible(self):
        """ Invoked to get the menu's visibility. """

        return self.adaptee.menuAction().isVisible()

    @visible.setter
    def visible(self, value):
        """ Invoked to set the menu's visibility. """

        self._update_visibility(value)

    @IMenu.views.getter
    def views(self):
        """ Invoked to get the views. """

        views = []
        for qaction in self.adaptee.actions():
            if qaction.isSeparator():
                item = ''
            elif isinstance(qaction, PlaceHolder):
                if qaction.occupied:
                    continue

                item = qaction.objectName()
            else:
                submenu = qaction.menu()
                item = IAction(qaction) if submenu is None else IMenu(submenu)

            views.append(item)

        return views

    @views.setter
    def views(self, value):
        """ Invoked to set the views. """

        # We handle this by observing the change.

    @observe('views')
    def __views_changed(self, change):

        qmenu = self.adaptee

        # FIXME: Remove old views.

        for item in change.new:
            item = unadapted(item)

            if isinstance(item, QAction):
                qmenu.addAction(item)
            elif isinstance(item, QMenu):
                qmenu.addMenu(item)
            elif item != '':
                qmenu.addAction(PlaceHolder(item, qmenu))
            else:
                qmenu.addSeparator()

        self._update_visibility(self._visible)

    def add_action(self, action):
        """ Try and add an action or action collection to the menu.

        :param action:
            is the action.
        :return:
            ``True`` if the action was added.  ``False`` is returned if the
            menu couldn't accommodate the action's desired positioning.
        """

        if isinstance(action, IActionCollection):
            action_collection = action

            # Within takes precedence.
            if action_collection.within == self.id:
                # Create a sub-menu if needed.
                if action_collection.text != '':
                    qmenu = QMenu(action_collection.text, self.adaptee,
                            objectName=action_collection.id)
                    self.adaptee.addMenu(qmenu)
                else:
                    qmenu = self.adaptee

                    # Make sure there is a separator each side.
                    qmenu.addSeparator()

                for action in action_collection.actions:
                    qmenu.addAction(
                            PlaceHolder.as_QAction(action, self.adaptee))

                if action_collection.text == '':
                    qmenu.addSeparator()
            else:
                if not PlaceHolder.add_action_collection(action_collection, self.adaptee):
                    return False
        else:
            qaction = unadapted(action)
            if action is qaction:
                action = IAction(qaction)

            # Within takes precedence.
            if action.within == self.id:
                self.adaptee.addAction(qaction)
            else:
                if not PlaceHolder.add_action(action, self.adaptee):
                    return False

        self._update_visibility(self._visible)

        return True

    def _update_visibility(self, visible):
        """ Update the visibility of the menu. """

        qmenu = self.adaptee

        if visible is None:
            visible = False

            for action in qmenu.actions():
                if action.isSeparator():
                    continue

                submenu = action.menu()
                if submenu is None:
                    # On macOS the quit action is in the system menu so ignore
                    # it.
                    if sys.platform == 'darwin' and action.menuRole() is QAction.MenuRole.QuitRole:
                        continue

                    if not isinstance(action, PlaceHolder):
                        visible = True
                else:
                    if submenu.menuAction().isVisible():
                        visible = True

        qmenu.menuAction().setVisible(visible)
