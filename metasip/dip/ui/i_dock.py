# Copyright (c) 2011 Riverbank Computing Limited.
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


from ..model import Enum, Instance, Str

from .i_action import IAction
from .i_single_view_container import ISingleViewContainer


class IDock(ISingleViewContainer):
    """ The IDock interface defines the API to be implemented by a dock. """

    # The action that will toggle the dock's visibility.
    action = Instance(IAction)

    # The dock area that the dock is initially placed in.
    area = Enum('left', 'right', 'top', 'bottom')

    # The identifier of an optional collection of actions that the action used
    # to toggle the dock visibility will be placed within.
    within = Str()
