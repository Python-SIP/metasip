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


@implements(IPlugin, IDisplay)
class WhatsThisToolPlugin(Model):
    """ The WhatsThisToolPlugin class is the plugin definition for the "What's
    This?" tool.
    """

    # The identifier of the plugin.
    id = 'dip.shell.tools.whats_this'

    # The name of the plugin.
    name = "What's This? tool plugin"

    def configure(self, plugin_manager):
        """ This is called when the plugin is enabled to ask that it configures
        itself.

        :param plugin_manager:
            the plugin manager.
        """

        # Create the tool instance.
        from ..tools.whats_this import WhatsThisTool
        tool = WhatsThisTool()

        # Contribute the tool.
        plugin_manager.contribute('dip.shell.tools', tool)
