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


from ...model import implements, Model
from ...plugins import IPlugin, Service
from ...ui import IDisplay

from .. import IShell


@implements(IPlugin, IDisplay)
class MainWindowShellPlugin(Model):
    """ The MainWindowShellPlugin class is the plugin definition for the main
    window based shell.
    """

    # The identifier of the plugin.
    id = 'dip.shell.shells.mainwindow'

    # The name of the plugin.
    name = "Main window shell plugin"

    def configure(self, plugin_manager):
        """ This is called when the plugin is enabled to ask that it configures
        itself.

        :param plugin_manager:
            the plugin manager.
        """

        # Create the shell instance.
        from ..shells.main_window import MainWindowShell
        service = MainWindowShell()()

        # Bind to the tools extension point.
        plugin_manager.bind_extension_point('dip.shell.tools', IShell(service),
                'tools')

        # Publish the service.
        plugin_manager.services.append(
                Service(interface=IShell, implementation=service))
