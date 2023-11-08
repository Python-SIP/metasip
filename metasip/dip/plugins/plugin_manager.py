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

from .i_plugin_manager import IPluginManager


class PluginManager(Singleton):
    """ The PluginManager class is a singleton that provides access to a
    default :term:`plugin manager`.
    """

    # The plugin manager instance.
    instance = Instance(IPluginManager)

    @instance.default
    def instance(self):
        """ Invoked to return the plugin manager. """

        from .default_plugin_manager import PluginManager

        return PluginManager()

    @classmethod
    def add_plugin(cls, plugin):
        """ Add a plugin to the plugin manager.

        :param plugin:
            is the plugin.
        """

        pluginmanager = cls().instance

        try:
            pluginmanager._dip_io_plugin_configured
        except AttributeError:
            from ..io import IoManager

            # Rather than have a i/o manager plugin, now that we know we have a
            # plugin-aware application we just configure the core i/o manager.
            iomanager = IoManager().instance

            pluginmanager.bind_extension_point('dip.io.codecs', iomanager,
                    'codecs')
            pluginmanager.bind_extension_point('dip.io.storage_factories',
                    iomanager, 'storage_factories')
            pluginmanager.bind_extension_point('dip.io.storage_policies',
                    iomanager, 'storage_policies')

            pluginmanager._dip_io_plugin_configured = True

        # Add the new plugin.
        pluginmanager.plugins.append(plugin)
