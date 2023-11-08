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


from ...model import implements, Model
from ...plugins import IPlugin
from ...ui import IDisplay

from .. import IDistributionManager


@implements(IPlugin, IDisplay)
class DistributionManagerPlugin(Model):
    """ The DistributionManagerPlugin class is the plugin definition for the
    configuration of the DistributionManager instance.
    """

    # The identifier of the plugin.
    id = 'dip.builder.DistributionManager'

    # The name of the plugin.
    name = "DIP builder distribution manager plugin"

    # The required plugins.
    requires = ['dip.builder.services.IDistributionManager']

    def configure(self, plugin_manager):
        """ Configure the plugin. """

        from ..distribution_manager import DistributionManager

        # Bind the IDistributionManager service to the DistributionsMaanger
        # singleton.
        plugin_manager.bind_service(IDistributionManager,
                DistributionManager(), 'instance')
