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


from ....model import implements, Model
from ....ui.actions import WhatsThisAction

from ... import ITool


@implements(ITool)
class WhatsThisTool(Model):
    """ The WhatsThisTool class is the default implementation of a :term:`tool`
    that implements the well known "What's This?" action.  This assumes that
    the toolkit supplies the behaviour as well as the action itself.
    """

    # The tool's identifier.
    id = 'dip.shell.tools.whats_this'

    # The action.
    whats_this_action = WhatsThisAction()
