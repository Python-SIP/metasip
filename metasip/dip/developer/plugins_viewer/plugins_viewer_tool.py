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


from ...shell import SimpleViewTool


class PluginsViewerTool(SimpleViewTool):
    """ The PluginsViewerTool implements a tool for displaying plugins. """

    # The identifier to be used for any action.
    action_id = 'dip.developer.view_plugins'

    # The tool's name.
    name = "Plugins"

    # The optional identifier of a collection of actions that any action will
    # be placed within.
    within = 'dip.ui.collections.view'

    @SimpleViewTool.view.default
    def view(self):
        """ The default view implementation. """

        from .plugins_viewer import PluginsViewer

        return PluginsViewer()
