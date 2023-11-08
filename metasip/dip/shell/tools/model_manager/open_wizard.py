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


from ....io import IoManager, IStorage, IStorageBrowser, IStorageLocation
from ....model import Any, Bool, Dict, Instance, observe
from ....ui import OptionList, Wizard, WizardController, WizardPage

from ... import IManagedModelTool

from .model_manager_tool import ModelManagerTool


class OpenWizard(Wizard):
    """ OpenWizard is an internal class that implements the wizard needed by
    the Open action when the user has to specify more than one piece of
    information.
    """

    # The browsers.  There is a browser for each valid model template/storage
    # combination.
    browsers = Dict()

    # The storage location.
    location = Instance(IStorageLocation)

    # The model template.
    model_template = Any()

    # The managed model manager using the wizard.
    model_manager = Instance(ModelManagerTool)

    # The current storage.
    storage = Instance(IStorage)

    # The tool.
    tool = Instance(IManagedModelTool)

    # Set if the controller should explicitly update the storage.
    update_storage = Bool(False)

    # Set if the controller should explicitly update the tool.
    update_tool = Bool(False)

    def __init__(self):
        """ Initialise the wizard factory. """

        # Create pages for those things we don't already know.

        io_manager_ui = IoManager.ui
        manager = self.model_manager

        pages = []

        if self.model_template is None:
            model_templates, labels = manager._resources.model_templates_for_open()

            page = WizardPage(
                    OptionList('model_template', allow_none=False,
                            labels=labels, options=model_templates,
                            sorted=True),
                    auto_form='never',
                    subtitle=manager.choose_open_model_prompt,
                    title=manager.choose_model_wizard_title,
                    id='dip.shell.open.model_page')

            pages.append(page)
        else:
            model_templates = [self.model_template]

        # Create the dict of browsers.
        for model_template in model_templates:
            for storage in manager._resources.storage_for_open(model_template):
                self.browsers[(model_template, storage)] = storage.ui.read_browser(default_location=self.location, hints=model_template)

        if manager._resources.are_multiple_storage_for_open():
            page = io_manager_ui.readable_storage_wizard_page('storage',
                    id='dip.shell.open.storage_page')
            pages.append(page)
        elif self.storage is None:
            self.update_storage = True

        page = io_manager_ui.readable_location_wizard_page(
                id='dip.shell.open.location_page')
        pages.append(page)

        if manager._resources.are_multiple_tools_for_open():
            page = WizardPage(
                    OptionList('tool', allow_none=False, sorted=True),
                    auto_form='never', subtitle=manager.choose_tool_prompt,
                    title=manager.choose_tool_wizard_title,
                    id='dip.shell.open.tool_page')
            pages.append(page)
        elif self.tool is None:
            self.update_tool = True

        super().__init__(*pages, title=manager.user_open_title)

    def execute(self):
        """ Create and execute the wizard.  Return True if the user accepted.
        """

        manager = self.model_manager

        self.controller_factory = lambda model, view: _OpenWizardController(
                model=model, view=view, model_manager=manager,
                browsers=self.browsers, update_storage=self.update_storage,
                update_tool=self.update_tool)

        wizard = self(model=self, parent=manager.shell)

        # Add the browsers to the location page.
        for view in wizard.views:
            if view.id == 'dip.shell.open.location_page':
                view.view.views = self.browsers.values()

        return wizard.execute()


class _OpenWizardController(WizardController):
    """ An internal class that updates the contents of various pages of the
    Open wizard that are dependent on the contents of other pages.
    """

    # Automatically update the model.
    auto_update_model = True

    # The browsers keyed by the tuple of model template and storage.
    browsers = Dict()

    # The managed model manager using the wizard.
    model_manager = Instance(ModelManagerTool)

    # Set if the controller should explicitly update the storage.
    update_storage = Bool()

    # Set if the controller should explicitly update the tool.
    update_tool = Bool()

    @observe('current_page')
    def __current_page_changed(self, change):
        """ Invoked when the wizard's current page changes. """

        page = change.old
        if page is not None:
            # This can happen when we are closing.
            if change.new is None:
                return

            if page.id == 'dip.shell.open.model_page':
                # These need to be explicitly updated if there is no
                # corresponding wizard page (because there will only ever be
                # one value) but the value is dependent on the model template.
                if self.update_storage:
                    self.model.storage = self.model_manager._resources.storage_for_open(self.model.model_template)[0]

                if self.update_tool:
                    self.model.tool = self.model_manager._resources.tools_for_open(self.model.model_template)[0]

        page = change.new
        if page is not None:
            if page.id == 'dip.shell.open.storage_page':
                # Update the storage list now that we know what the model
                # template is.
                self.storage_editor.options = self.model_manager._resources.storage_for_open(self.model.model_template)

            elif page.id == 'dip.shell.open.location_page':
                # Update the storage browser now that we know what model
                # template and storage has been selected.
                page.view.current_view = self._current_browser()

            elif page.id == 'dip.shell.open.tool_page':
                # Update the list of tools now that we know what the model
                # template is.
                self.tool_editor.options = self.model_manager._resources.tools_for_open(self.model.model_template)

    def validate_view(self):
        """ Reimplemented to validate the location page differently. """

        if self.current_page is None:
            return ''

        if self.current_page.id != 'dip.shell.open.location_page':
            return ''

        storage_browser = IStorageBrowser(self._current_browser())

        # It doesn't matter if it is invalid.
        self.model.location = storage_browser.location

        return storage_browser.invalid_reason

    @browsers.setter
    def browsers(self, value):
        """ Invoked to set the dictionary of browsers. """

        # Re-validate when any location changes.
        for browser in value.values():
            observe('location', IStorageBrowser(browser), self.validate)

    def _current_browser(self):
        """ Return the current browser. """

        return self.browsers[(self.model.model_template, self.model.storage)]
