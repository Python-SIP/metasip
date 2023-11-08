# Copyright (c) 2012 Riverbank Computing Limited.
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
from .i_object import IObject


class IActionCollection(IObject):
    """ The IActionCollection interface defines the API to be implemented by an
    :term:`action` collection.
    """

    # The actions contained in the collection.
    actions = List(Instance(IAction, Str()))

    # The text of the action collection.
    text = Str()

    # The identifier of an optional action collection that this action
    # collection will be placed within.  If it is not specified then the
    # toolkit will place it automatically.
    within = Str()
