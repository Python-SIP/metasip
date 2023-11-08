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


from PyQt5.QtWidgets import QTreeView

from .....model import adapt
from .....settings import ISettings

from .widget_adapter import WidgetAdapter


@adapt(QTreeView, to=ISettings)
class QTreeViewISettingsAdapter(WidgetAdapter):
    """ An adapter to implement ISettings for a QTreeView. """

    def restore(self, settings_manager):
        """ Restore the settings obtained from a settings manager.

        :param settings_manager:
            is the settings manager.
        """

        value = settings_manager.read_value('header')
        if value is not None:
            self.adaptee.header().restoreState(value)

    def save(self, settings_manager):
        """ Save the settings to a settings manager.

        :param settings_manager:
            is the settings manager.
        """

        settings_manager.write_value('header',
                self.adaptee.header().saveState())
