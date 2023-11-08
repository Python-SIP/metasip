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


from ....model import Any, Instance, observe
from ....ui import OptionList, Wizard, WizardController, WizardPage

from ... import IManagedModelTool

from .model_manager_tool import ModelManagerTool


class NewWizard(Wizard):
    """ NewWizard is an internal class that implements the wizard needed by the
    New action when the user has to specify more than one piece of information.
    """

    # The model template.
    model_template = Any()

    # The managed model manager using the wizard.
    model_manager = Instance(ModelManagerTool)

    # The tool.
    tool = Instance(IManagedModelTool)

    def __init__(self):
        """ Initialise the wizard factory. """

        manager = self.model_manager

        model_templates, labels = manager._resources.model_templates_for_new()

        model_page = WizardPage(
                OptionList('model_template', allow_none=False, labels=labels,
                        options=model_templates, sorted=True),
                auto_form='never', subtitle=manager.choose_new_model_prompt,
                title=manager.choose_model_wizard_title)

        tool_page = WizardPage(
                OptionList('tool', allow_none=False, sorted=True),
                auto_form='never', subtitle=manager.choose_tool_prompt,
                title=manager.choose_tool_wizard_title,
                id='dip.shell.new.tool_page')

        super().__init__(model_page, tool_page, title=manager.user_new_title)

    def execute(self):
        """ Create and execute the wizard.  Return True if the user accepted.
        """

        self.controller_factory = lambda model, view: _NewWizardController(
                model=model, view=view, model_manager=self.model_manager)

        wizard = self(model=self, parent=self.model_manager.shell)

        return wizard.execute()


class _NewWizardController(WizardController):
    """ An internal class that updates the contents of various pages of the
    New wizard that are dependent on the contents of other pages.
    """

    # Automatically update the model.
    auto_update_model = True

    # The managed model manager using the wizard.
    model_manager = Instance(ModelManagerTool)

    @observe('current_page')
    def __current_page_changed(self, change):
        """ Invoked when the wizard's current page changes. """

        if change.new is not None:
            if change.new.id == 'dip.shell.new.tool_page':
                # Update the list of tools now that we know what the model
                # factory is.
                self.tool_editor.options = self.model_manager._resources.tools_for_new(self.model.model_template)
