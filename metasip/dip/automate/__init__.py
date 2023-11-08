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


""" The :mod:`dip.automate` module contains a collection of classes that allow
an application to be automated.
"""


from .i_automated import IAutomated
from .i_automated_action_trigger import IAutomatedActionTrigger
from .i_automated_dialog import IAutomatedDialog
from .i_automated_editor import IAutomatedEditor
from .i_automated_list_editor import IAutomatedListEditor
from .i_automated_option_selector import IAutomatedOptionSelector
from .i_automated_shell import IAutomatedShell
from .i_automated_tab_bar import IAutomatedTabBar
from .i_automated_table_editor import IAutomatedTableEditor
from .i_automated_trigger import IAutomatedTrigger

from .automation_commands import AutomationCommands
from .exceptions import AutomationError
from .robot import Robot

# Make sure all adapters get registered
from . import toolkits
del toolkits
