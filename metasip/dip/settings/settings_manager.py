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


from ..model import Instance, Singleton

from .i_settings_manager import ISettingsManager


class SettingsManager(Singleton):
    """ The SettingsManager class is a singleton that provides access to a
    default settings manager.
    """

    # The settings manager instance.
    instance = Instance(ISettingsManager)

    @instance.default
    def instance(self):
        """ Invoked to return the settings manager. """

        from .default_settings_manager import SettingsManager

        return SettingsManager()
