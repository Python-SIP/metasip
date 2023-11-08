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


import functools

# FIXME: replace with proper toolkit support.
from ... import TOOLKIT
if TOOLKIT == 'qt4':
    from PyQt4.QtGui import QTreeWidget, QTreeWidgetItem
else:
    from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem

from ...model import observe
from ...plugins import PluginManager
from ...ui import IDisplay


class PluginsViewer(QTreeWidget):
    """ The PluginsViewer class is a widget that implements a read-only
    visualisation of all plugins.
    """

    def __init__(self):
        """ Initialise the viewer. """

        super().__init__()

        self.setRootIsDecorated(False)
        self.setHeaderLabels(["Identifier", "Plugin", "Enabled", "Requires"])

        pluginmanager = PluginManager().instance
        self._new_plugins(pluginmanager.plugins)
        observe('plugins', pluginmanager, self.__plugins_changed)

    def __plugins_changed(self, change):
        """ Invoked when the list of plugins changes. """

        # At the moment plugins can only be added.
        self._new_plugins(change.new)

    def _new_plugins(self, plugins):
        """ Add a list of new plugins. """

        for plugin in plugins:
            tool_tip = str(plugin)

            idisplay = IDisplay(plugin, exception=False)
            name = '' if idisplay is None else idisplay.name
            if name == '':
                name = tool_tip

            itm = QTreeWidgetItem(self,
                    [plugin.id, name, "Yes" if plugin.enabled else "No",
                            ", ".join(plugin.requires)])
            itm.setToolTip(1, tool_tip)

            observe('enabled', plugin,
                    functools.partial(self.__plugin_state_changed, itm))

    def __plugin_state_changed(self, itm, change):
        """ Invoked when the enabled state of a plugin changes. """

        itm.setText(2, "Yes" if change.new else "No")
