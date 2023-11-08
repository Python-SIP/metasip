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


from PyQt5.QtWidgets import QWizard

from .....model import adapt, notify_observers, unadapted
from .....ui import IWizard, IWizardPage

from .container_adapters import ContainerWidgetAdapter


@adapt(QWizard, to=IWizard)
class QWizardIWizardAdapter(ContainerWidgetAdapter):
    """ An adapter to implement IWizard for a QWizard. """

    def configure(self, properties):
        """ Configure the widget. """

        wizard = self.adaptee

        wizard.currentIdChanged.connect(self._current_id_changed)
        wizard.button(QWizard.FinishButton).clicked.connect(self._on_finished)

        super().configure(properties)

    def execute(self):
        """ Execute the wizard.

        :return:
            ``True`` if the user accepted the wizard.
        """

        return bool(self.adaptee.exec())

    @IWizard.current_page.getter
    def current_page(self):
        """ Invoked to get the current page. """

        return self.adaptee.currentPage()

    @current_page.setter
    def current_page(self, value):
        """ Invoked to set the current page. """

        wizard = self.adaptee

        qpage = unadapted(value)

        for id in wizard.pageIds():
            if wizard.page(id) is qpage:
                wizard.setStartId(id)
                wizard.restart()
                break

    @IWizard.views.getter
    def views(self):
        """ Invoked to get the views (i.e. pages). """

        wizard = self.adaptee

        # The model getter will convert this to a tuple of IWizardPages.
        return [wizard.page(page_id) for page_id in wizard.pageIds()]

    @views.setter
    def views(self, value):
        """ Invoked to set the views (i.e. pages). """

        wizard = self.adaptee

        # Remove any existing pages.
        for page_id in wizard.pageIds():
            wizard.removePage(page_id)

        # Add the new pages.
        first_page = None
        final_page = wizard.options() & QWizard.HaveFinishButtonOnEarlyPages

        for page in value:
            qpage = unadapted(page)

            if first_page is None:
                first_page = page

            if final_page:
                qpage.setFinalPage(True)

            wizard.addPage(qpage)

        self._tk_old_page = None
        self.current_page = first_page

    def _current_id_changed(self, id):
        """ Invoked then the current page changes. """

        old_page = self._tk_old_page

        qpage = self.adaptee.page(id)
        if qpage is None:
            new_page = self._tk_old_page = None
        else:
            new_page = self._tk_old_page = IWizardPage(qpage)

        notify_observers('current_page', self, new_page, old_page)

    def _on_finished(self):
        """ Invoked when the Finish button is clicked. """

        self.finished = True
