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


from PyQt4.QtGui import QAction, QMenu

from .....model import unadapted
from .....ui import IMenu


class PlaceHolder(QAction):
    """ An invisible place holder action.  It also acts as a namespace for some
    related utility functions.
    """

    def __init__(self, id, parent):
        """ Initialise the place holder. """

        super().__init__(parent, objectName=id, visible=False)

        # The place isn't occupied by a real action.
        self.occupied = False

    @classmethod
    def add_action(cls, action, widget):
        """ Try and add an action to a widget.

        :param action:
            is the action.
        :param widget:
            is the widget.
        :return:
            ``True`` if the action was added.  ``False`` is returned if the
            widget couldn't accommodate the action's desired positioning.
        """

        qaction = unadapted(action)

        action_id = qaction.objectName()

        for act in widget.actions():
            if act.isSeparator():
                continue

            submenu = act.menu()
            if submenu is None:
                if act.objectName() == action_id:
                    if not isinstance(act, cls):
                        raise ValueError(
                                "an action '{0}' already exists".format(
                                        action_id))

                    # No need to check if it is occupied because the occupier
                    # would have been found first.
                    act.occupied = True

                    widget.insertAction(act, qaction)

                    return True
            else:
                if IMenu(submenu).add_action(action):
                    return True

        return False

    @classmethod
    def add_action_collection(cls, action_collection, widget):
        """ Try and add an action collection to a widget.

        :param action_collection:
            is the action collection.
        :param widget:
            is the widget.
        :return:
            ``True`` if the collection was added.  ``False`` is returned if the
            widget couldn't accommodate the collection's desired positioning.
        """

        for act in widget.actions():
            if act.isSeparator():
                continue

            submenu = act.menu()
            if submenu is None:
                if act.objectName() == action_collection.id:
                    if not isinstance(act, cls) or act.occupied:
                        raise ValueError(
                                "an action collection '{0}' already "
                                "exists".format(action_collection.id))

                    act.occupied = True

                    # Create a sub-menu if needed.
                    if action_collection.text != '':
                        menu = cls.as_QMenu(action_collection, widget)
                        widget.insertMenu(act, menu)
                    else:
                        # Make sure there is a separator each side.
                        widget.addSeparator()

                        for action in reversed(action_collection.actions):
                            widget.insertAction(act,
                                    cls.as_QAction(action, widget))

                        widget.addSeparator()

                    return True
            else:
                if IMenu(submenu).add_action(action_collection):
                    return True

        return False

    @classmethod
    def as_QMenu(cls, action_collection, widget):
        """ Make sure an action collection is a QMenu. """

        menu = QMenu(action_collection.text, widget,
                objectName=action_collection.id)

        for action in action_collection.actions:
            menu.addAction(cls.as_QAction(action, menu))

        return menu

    @classmethod
    def as_QAction(cls, action, widget):
        """ Make sure an action is a QAction. """

        qaction = unadapted(action)

        if isinstance(qaction, QAction):
            return qaction

        if action == '':
            qaction = QAction(widget)
            qaction.setSeparator(True)
        else:
            qaction = cls(action, widget)

        return qaction
