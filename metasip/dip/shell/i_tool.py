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


from ..model import Instance, Interface, List, Str
from ..ui import IAction, IActionCollection, IView


class ITool(Interface):
    """ The ITool interface defines the API to be implemented by a
    :term:`tool`.
    """

    # The tool's actions.  Any initial actions will be automatically added to
    # the shell.  If there are none then the tool is introspected for any
    # :class:`~dip.ui.ActionCollection` attributes and then any
    # :class:`~dip.ui.Action` attributes.
    actions = List(Instance(IAction, IActionCollection))

    # The tool's current view.  It will be ``None`` if the shell's current view
    # does not belong to this tool.
    current_view = Instance(IView)

    # The tool's identifier.
    id = Str()

    # The shell that the tool is attached to.
    shell = Instance('.IShell')

    # The tool's views.  Any initial views will be automatically added to the
    # shell.
    views = List(IView)
