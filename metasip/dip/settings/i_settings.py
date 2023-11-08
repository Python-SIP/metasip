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


from ..model import Interface, Str


class ISettings(Interface):
    """ The ISettings class defines the interface that should be implemented by
    an object, often a view, that reads and writes user settings.
    """

    # The identifier of the setting.
    id = Str()

    def restore(self, settings_manager):
        """ Restore the settings obtained from a settings manager.

        :param settings_manager:
            is the settings manager.
        """

    def save(self, settings_manager):
        """ Save the settings to a settings manager.

        :param settings_manager:
            is the settings manager.
        """
