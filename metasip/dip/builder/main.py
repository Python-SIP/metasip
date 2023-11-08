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


import sys

from ..plugins import PluginManager
from ..shell import IManagedModelTool, IShell
from ..ui import Application, IApplication, IView


def main():
    """ The setuptools entry point for the builder application. """

    # Create the toolkit specific application.
    app = Application()

    # Add dip provided plugins for a shell, tools and storage.
    from ..shell.plugins import (DirtyToolPlugin, MainWindowShellPlugin,
            ModelManagerToolPlugin, QuitToolPlugin, WhatsThisToolPlugin)
    PluginManager.add_plugin(MainWindowShellPlugin())
    PluginManager.add_plugin(ModelManagerToolPlugin())
    PluginManager.add_plugin(DirtyToolPlugin())
    PluginManager.add_plugin(QuitToolPlugin())
    PluginManager.add_plugin(WhatsThisToolPlugin())

    from ..io.plugins import FilesystemStoragePlugin
    PluginManager.add_plugin(FilesystemStoragePlugin())

    # Add the plugins that implement this application.
    from ..builder.plugins import (IBuilderProjectCodecPlugin,
            IBuilderProjectFactoryPlugin, IBuilderProjectToolPlugin,
            CreateApplicationToolPlugin, CreateDistributionToolPlugin,
            DistributionManagerPlugin, IDistributionManagerServicePlugin,
            DistutilsDistributionPlugin)
    PluginManager.add_plugin(IBuilderProjectCodecPlugin())
    PluginManager.add_plugin(IBuilderProjectFactoryPlugin())
    PluginManager.add_plugin(IBuilderProjectToolPlugin())
    PluginManager.add_plugin(CreateApplicationToolPlugin())
    PluginManager.add_plugin(IDistributionManagerServicePlugin())
    PluginManager.add_plugin(DistributionManagerPlugin())
    PluginManager.add_plugin(CreateDistributionToolPlugin())
    PluginManager.add_plugin(DistutilsDistributionPlugin())

    # Ask for a shell for the user interface.
    ui = PluginManager.service(IShell)

    # Configure the shell and project editor to only handle one project at a
    # time.
    ishell = IShell(ui)

    ishell.main_area_policy = 'single'
    ishell.title_template = "DIP Builder - [view][*]"

    for tool in ishell.tools:
        imanagedmodeltool = IManagedModelTool(tool, exception=False)

        if imanagedmodeltool is not None and imanagedmodeltool.id == 'dip.builder.tools.project_editor':
            imanagedmodeltool.model_policy = 'one'

    # Handle the command line.
    if len(sys.argv) == 2:
        ishell.open('dip.builder.tools.project_editor', sys.argv[1],
                'dip.builder.formats.project')

    elif len(sys.argv) > 2:
        Application.warning("Usage Error",
                "At most one command line argument is expected.")

    # Make the shell visible.
    IView(ui).visible = True

    # Enter the event loop.
    return IApplication(app).execute()
