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


""" The :mod:`dip.ui.actions` module implements factories for a number of
well known :term:`actions<action>`.
"""


from .close_action import CloseAction
from .new_action import NewAction
from .open_action import OpenAction
from .quit_action import QuitAction
from .save_action import SaveAction
from .save_as_action import SaveAsAction
from .whats_this_action import WhatsThisAction
