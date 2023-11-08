# Copyright (c) 2017 Riverbank Computing Limited.
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


from PyQt5.QtCore import QSettings

from .....model import adapt, Adapter
from .....settings import ISettingsStorage


@adapt(QSettings, to=ISettingsStorage)
class QSettingsISettingsStorageAdapter(Adapter):
    """ An adapter to implement ISettingsStorage for a QSettings. """

    def begin_group(self, group):
        """ Begin a group.

        :param group:
            is the name of the group.
        """

        self.adaptee.beginGroup(group)

    def end_group(self):
        """ End the current group. """

        self.adaptee.endGroup()

    def flush(self):
        """ Ensure that all settings changes are written to persistent storage.
        """

        self.adaptee.sync()

    def read_value(self, name):
        """ Read the value of a setting.

        :param name:
            is the name of the setting.
        :return:
            the value of the setting, or None if there is no such setting.
        """

        return self.adaptee.value(name)

    def write_value(self, name, value):
        """ Write the value of a setting.

        :param name:
            is the name of the setting.
        :param value:
            is the value of the setting.  If this is None then the setting is
            removed.
        """

        if value is None:
            self.adaptee.remove(name)
        else:
            self.adaptee.setValue(name, value)
