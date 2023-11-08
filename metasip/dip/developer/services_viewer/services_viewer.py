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


# FIXME: replace with proper toolkit support.
from ... import TOOLKIT
if TOOLKIT == 'qt4':
    from PyQt4.QtGui import QTreeWidget, QTreeWidgetItem
else:
    from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem

from ...model import observe
from ...plugins import PluginManager
from ...ui import IDisplay


class ServicesViewer(QTreeWidget):
    """ The ServicesViewer class is a widget that implements a read-only
    visualisation of all services.
    """

    def __init__(self):
        """ Initialise the viewer. """

        super().__init__()

        self.setHeaderLabels(["Interface", "Implementation"])

        pluginmanager = PluginManager().instance
        self._new_services(pluginmanager.services)
        observe('services', pluginmanager, self.__services_changed)

    def __services_changed(self, change):
        """ Invoked when the list of services changes. """

        # At the moment services can only be added.
        self._new_services(change.new)

    def _new_services(self, services):
        """ Add a list of new services. """

        for service in services:
            interface_full_name = str(service.interface)

            for i in range(self.topLevelItemCount()):
                itm = self.topLevelItem(i)
                if itm.toolTip(0) == interface_full_name:
                    break
            else:
                itm = QTreeWidgetItem(self, [service.interface.__name__])
                itm.setToolTip(0, interface_full_name)

            tool_tip = str(service.implementation)

            idisplay = IDisplay(service.implementation, exception=False)
            name = '' if idisplay is None else idisplay.name
            if name == '':
                name = tool_tip

            child_itm = QTreeWidgetItem(itm, ['', name])
            child_itm.setToolTip(1, tool_tip)
