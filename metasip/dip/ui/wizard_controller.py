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


from ..model import Instance, observe

from .i_container import IContainer
from .controller import Controller
from .i_wizard import IWizard
from .i_wizard_page import IWizardPage


class WizardController(Controller):
    """ The WizardController class is a :term:`controller` for handling
    wizards.
    """

    # This determines if the controller should automatically update the model
    # when the user changes the value of an editor.  If it is not set then the
    # model is only updated when the current page changes or when the wizard is
    # completed.
    auto_update_model = False

    # The current page.
    current_page = Instance(IWizardPage)

    # The view.
    view = Instance(IWizard)

    def update_view(self):
        """ Reimplemented to disable the accept button if the view is invalid.
        """

        if self.current_page is not None:
            self.current_page.acceptable = self.is_valid()

    def editors_to_validate(self):
        """ Return the sequence of editors to validate.

        :return:
            the sequence of editors.
        """

        return [] if self.current_page is None else self._page_editors(self.current_page)

    @Controller.view.setter
    def view(self, value):
        """ Invoked to set the view. """

        # Observe the wizard's current page.
        observe('current_page', value, self.__current_page_changed)

        # Observe the wizard's finished trigger.
        observe('finished', value, self.__on_finished)

        # Initialise the current page.
        self.current_page = value.current_page

    def __current_page_changed(self, change):
        """ Invoked when the current page changes. """

        # Update the model for any previous page.
        self._update_model()

        self.current_page = change.new

        self.validate()

    def __on_finished(self, change):
        """ Invoked when the wizard's finished trigger is pulled. """

        self._update_model()

    def _update_model(self):
        """ Update the model if it is not being done automatically. """

        # Update the model if not already done.
        if not self.auto_update_model:
            self.update_model()

    def _page_editors(self, page):
        """ A generator for the editors that are in a page. """

        for view in page.views:
            if view in self.editors:
                yield view

            container = IContainer(view, exception=False)
            if container is not None:
                for editor in self._page_editors(container):
                    yield editor
