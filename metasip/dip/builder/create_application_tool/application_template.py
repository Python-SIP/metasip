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


from ...model import implements, Model
from ...ui import (Form, ListEditor, MessageArea, Stretch, VBox, Wizard,
        IWizard, WizardPage)

from .. import IApplicationTemplate

from .python_class import PythonClass


@implements(IApplicationTemplate)
class ApplicationTemplate(Model):
    """ The ApplicationTemplate class is the default implementation of an
    application template.
    """

    # The wizard used to get the input from the user.
    wizard = Wizard(
            WizardPage(
                VBox(
                    Form(
                        'script_name',
                        'title_bar_text',
                        'interpreter'
                    ),
                    Stretch(),
                    MessageArea()
                ),
                title="Application Script",
                subtitle="Enter the details of the script to create."
            ),
            WizardPage(
                VBox(
                    ListEditor('plugins',
                            columns=['class_name', 'module_name'],
                            item_factory=lambda: PythonClass(
                                    class_name="NewPluginClass",
                                    module_name="new.module")),
                    Stretch(),
                    MessageArea()
                ),
                title="Plugins",
                subtitle="Enter the details of the application plugins.  " \
                        "Order is important as some plugins may depend on " \
                        "others."
            )
        )

    def populate(self, title, parent):
        """ Populate the application template with input from the user.

        :param title:
            is the window title to use.
        :param parent:
            is the parent view.
        :return:
            ``True`` if the template is populated.
        """

        ui = self.wizard(self, parent=parent, title=title)

        return IWizard(ui).execute()

    @IApplicationTemplate.plugins.default
    def plugins(self):
        """ Create the default list of plugins. """

        return [
                PythonClass(class_name='MainWindowShellPlugin',
                        module_name='dip.shell.plugins'),
                PythonClass(class_name='ModelManagerToolPlugin',
                        module_name='dip.shell.plugins'),
                PythonClass(class_name='DirtyToolPlugin',
                        module_name='dip.shell.plugins'),
                PythonClass(class_name='QuitToolPlugin',
                        module_name='dip.shell.plugins'),
                PythonClass(class_name='WhatsThisToolPlugin',
                        module_name='dip.shell.plugins'),
                PythonClass(class_name='FilesystemStoragePlugin',
                        module_name='dip.io.plugins')]
