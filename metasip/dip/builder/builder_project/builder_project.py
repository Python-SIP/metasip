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


import os
import stat
import sys

from ...model import implements, Model

from .. import IBuilderProject


@implements(IBuilderProject)
class BuilderProject(Model):
    """ The BuilderProject class is the default implementation of a dip builder
    project.
    """

    _mode_flags = stat.S_IRWXU|stat.S_IRGRP|stat.S_IXGRP|stat.S_IROTH|stat.S_IXOTH

    def create_application(self, template):
        """ Create an application based on a template.

        :param template:
            is the template which will be an implementation of the
            :class:`~dip.builder.IApplicationTemplate` interface.
        """

        fout = open(template.script_name, 'w', encoding='utf8')

        if template.interpreter != '':
            fout.write(
                    _python_interpreter.format(
                            interpreter=template.interpreter))

        header = self.file_header_text.strip()
        if header != '':
            for line in header.split('\n'):
                fout.write("# " + line + "\n")

            fout.write("\n\n")

        fout.write(_imports)

        if len(template.plugins) > 0:
            fout.write("# Import the plugins.\n")

            # Keep all imports from the same module together.
            imports = {}
            for plugin in template.plugins:
                classes = imports.setdefault(plugin.module_name, [])
                classes.append(plugin.class_name)

            for module, plugins in imports.items():
                fout.write(
                        _plugin_imports.format(module_name=module,
                                plugins=", ".join(plugins)))

        fout.write(_application_instance)

        if len(template.plugins) > 0:
            fout.write("\n# Create and add the plugins.\n")

            for plugin in template.plugins:
                fout.write(_plugin.format(class_name=plugin.class_name))

        fout.write(_start.format(title=template.title_bar_text))

        fout.close()

        # Make it executable.
        os.chmod(template.script_name, self._mode_flags)


_python_interpreter = """#!{interpreter}


"""


_imports = """from dip.plugins import PluginManager
from dip.ui import Application, IApplication, IView

"""


_application_instance = """

# Create the application instance.
app = Application()
"""


_plugin_imports = """from {module_name} import {plugins}
"""


_plugin = """PluginManager.add_plugin({class_name}())
"""


_start = """
# Get the shell.
from dip.shell import IShell
ui = PluginManager.service(IShell)

# Display the shell.
iview = IView(ui)
iview.title = "{title}"
iview.visible = True

# Enter the event loop.
IApplication(app).execute()
"""
