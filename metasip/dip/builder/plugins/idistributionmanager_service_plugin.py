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

from .. import IDistributionManager


@implements(IPlugin, IDisplay)
class IDistributionManagerServicePlugin(Model):
    """ The IDistributionManagerServicePlugin class is the plugin definition
    for the default IDistributionManager service.
    """

    # The identifier of the plugin.
    id = 'dip.builder.services.IDistributionManager'

    # The name of the plugin.
    name = "DIP builder distribution manager service plugin"

    def configure(self, plugin_manager):
        """ Configure the plugin. """

        # Create the distribution manager instance.
        from ..default_distribution_manager import DistributionManager
        service = DistributionManager()

        # Bind to the distributions extension point
        plugin_manager.bind_extension_point('dip.builder.distributions',
                IDistributionManager(service), 'distributions')

        # Publish the service.
        plugin_manager.services.append(
                Service(interface=IDistributionManager,
                        implementation=service))
