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


from ..model import Interface


class ISettingsManager(Interface):
    """ The ISettingsManager interface defines the API of a settings manager.
    """

    def load(self, organization, application=None):
        """ Load the application's settings.

        :param organization:
            is the name of the organization.  It is recommended that this is a
            FQDN.
        :param application:
            is the name of the application.  It will default to the base name
            of sys.argv[0] with any extension removed.
        """

    def restore(self, models):
        """ Restore the settings for a sequence of models.  If no settings have
        been loaded, i.e. :meth:`~dip.settings.ISettingsManager.load` has not
        been called, then this has no effect.

        :param models:
            is the sequence of models.  Any model that does not implement
            :class:`~dip.settings.ISettings` is ignored.
        """

    def save(self, models):
        """ Save the settings for a sequence of models.  If no settings have
        been loaded, i.e. :meth:`~dip.settings.ISettingsManager.load` has not
        been called, then this has no effect.

        :param models:
            is the sequence of models.  Any model that does not implement
            :class:`~dip.settings.ISettings` is ignored.
        """

    def read_value(self, name):
        """ Read the value of a setting.

        :param name:
            is the name of the setting.
        :return:
            the value of the setting, or None if there is no such setting.
        """

    def write_value(self, name, value):
        """ Write the value of a setting.

        :param name:
            is the name of the setting.
        :param value:
            is the value of the setting.  If this is None then the setting is
            removed.
        """
