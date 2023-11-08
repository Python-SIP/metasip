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


""" The :mod:`dip.settings` module implements the infrastructure for
application specific persistent storage typically used for user settings.
"""


from .i_settings import ISettings
from .i_settings_manager import ISettingsManager
from .i_settings_storage import ISettingsStorage

from .settings_manager import SettingsManager

# Make sure adapters get registered.
from .ieditor_isettings_adapter import IEditorISettingsAdapter
del IEditorISettingsAdapter

from . import toolkits
del toolkits
