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


from ...model import Any, Bool, Dict, Instance, List, observe
from ...ui import Wizard, WizardController

from .. import IIoManagerUi, IStorage, IStorageLocation


class LocationWizard(Wizard):
    """ LocationWizard is an internal class that implements the wizard needed
    when the user has to specify both the storage and the location within the
    chosen storage.
    """

    # Set if the wizard is asking for readable storage.
    reading = Bool(True)

    # The hints.
    hints = Any()

    # The storage location.
    location = Instance(IStorageLocation)

    # The current storage.
    storage = Instance(IStorage)

    # The list of storage instances.
    storage_list = List(IStorage)

    # The i/o manager user interface using the wizard.
    ui = Instance(IIoManagerUi)

    def __init__(self):
        """ Initialise the wizard. """

        if self.reading:
            storage_page = self.ui.readable_storage_wizard_page(
                    'storage', storage_list=self.storage_list)

            location_page = self.ui.readable_location_wizard_page(
                    id='dip.io.location.location_page')
        else:
            storage_page = self.ui.writeable_storage_wizard_page(
                    'storage', storage_list=self.storage_list)

            location_page = self.ui.writeable_location_wizard_page(
                    id='dip.io.location.location_page')

        super().__init__(storage_page, location_page)

    def execute(self, parent):
        """ Create and execute the wizard.  Return True if the user accepted.
        """

        # Create browsers for the storage and determine the current storage if
        # there is an initial location.
        browsers = {}
        browser_list = []

        for storage in self.storage_list:
            if self.location is not None and self.location.storage is storage:
                self.storage = storage

            browser = storage.ui.write_browser(default_location=self.location,
                    hints=self.hints)
            browsers[storage] = browser
            browser_list.append(browser)

        self.controller_factory = lambda model, view: _WizardController(
                model=model, view=view, browsers=browsers)

        wizard = self(model=self, parent=parent)

        wizard.views[1].view.views = browser_list

        return wizard.execute()


class _WizardController(WizardController):
    """ An internal class that updates the contents of various pages of the
    location wizard that are dependent on the contents of other pages.
    """

    # Automatically update the model.
    auto_update_model = True

    # The browsers keyed by storage.
    browsers = Dict()

    @observe('current_page')
    def __page_changed(self, change):
        """ Invoked when the wizard's current page changes. """

        if change.new is not None:
            page = change.new

            if page.id == 'dip.io.location.location_page':
                # Update the storage browser now that we know what storage has
                # been selected.
                page.view.current_view = self._current_browser()

    def validate_view(self):
        """ Reimplemented to validate the location page differently. """

        if self.current_page is None:
            return ''

        if self.current_page.id != 'dip.io.location.location_page':
            return ''

        browser = self._current_browser()

        # It doesn't matter if it is invalid.
        self.model.location = browser.location

        return browser.invalid_reason

    @browsers.setter
    def browsers(self, value):
        """ Invoked to set the dictionary of browsers. """

        # Re-validate when any location changes.
        for browser in value.values():
            observe('location', browser, self.validate)

    def _current_browser(self):
        """ Return the current browser. """

        return self.browsers[self.model.storage]
