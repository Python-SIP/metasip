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


""" The :mod:`dip.shell` module implements the infrastructure for defining and
interfacing with a :term:`shell`.

Plugins must provide appropriate support for the following extension points:

``dip.shell.model_factories``
    This must be supported by any plugin that configures an object implementing
    the :class:`dip.shell.IModelManagerTool` interface.  A contribution must be
    a callable.

``dip.shell.tools``
    This must be supported by any plugin that configures an object implementing
    the :class:`dip.shell.IShell` interface.  A contribution must implement the
    :class:`dip.shell.ITool` interface.
"""


from .i_action_hints import IActionHints
from .i_area_hints import IAreaHints
from .i_close_view_veto import ICloseViewVeto
from .i_dirty import IDirty
from .i_managed_model import IManagedModel
from .i_managed_model_tool import IManagedModelTool
from .i_model_manager_tool import IModelManagerTool
from .i_open_model import IOpenModel
from .i_quit_veto import IQuitVeto
from .i_shell import IShell
from .i_tool import ITool

from .base_managed_model_tool import BaseManagedModelTool
from .base_shell_adapter import BaseShellAdapter
from .base_shell_factory import BaseShellFactory
from .simple_view_tool import SimpleViewTool

# Make sure all adapters get registered.
from . import imanagedmodel_idisplay_adapter
del imanagedmodel_idisplay_adapter

from . import toolkits
del toolkits
