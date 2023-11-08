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


from ..model import Bool, Instance, List, Str

from .i_action import IAction
from .i_container import IContainer


class IMenu(IContainer):
    """ The IMenu interface defines the API to be implemented by a menu. """

    # The visibility of the menu.  If this is None then the menu will be
    # visible only when it has some content.
    visible = Bool(None, allow_none=True)

    # The menu's contents.  An empty string means a separator.
    views = List(Instance(IAction, 'dip.ui.IMenu', Str()))

    def add_action(self, action):
        """ Try and add an action or action collection to the menu.

        :param action:
            is the action.
        :return:
            ``True`` if the action was added.  ``False`` is returned if the
            menu couldn't accommodate the action's desired positioning.
        """
