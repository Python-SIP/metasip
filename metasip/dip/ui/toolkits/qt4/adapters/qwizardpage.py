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


from PyQt4.QtGui import QWizardPage

from .....model import adapt, Bool
from .....ui import IWizardPage

from .single_view_container_adapters import SingleViewContainerLayoutAdapter


@adapt(QWizardPage, to=IWizardPage)
class QWizardPageIWizardPageAdapter(SingleViewContainerLayoutAdapter):
    """ An adapter to implement IWizardPage for a QWizardPage. """

    # This is set if the controller says the page is acceptable.
    _tk_acceptable = Bool(True)

    def configure(self, properties):
        """ Configure the widget. """

        # The controller maintains the 'acceptable' attribute which must be
        # returned by QWizardPage.isComplete().  We would normally reimplement
        # this in a sub-class, but we allow the binding of a plain QWizardPage
        # so we monkey patch it instead.
        def isComplete():
            # Note that we don't use the acceptable attribute, or its shadow,
            # because it will be set too late.
            return self._tk_acceptable

        self.adaptee.isComplete = isComplete

        super().configure(properties)

    @IWizardPage.acceptable.setter
    def acceptable(self, value):
        """ Invoked to set the acceptable state. """

        # Save the state.
        self._tk_acceptable = value

        self.adaptee.completeChanged.emit()

    @IWizardPage.subtitle.getter
    def subtitle(self):
        """ Invoked to get the sub-title. """

        return self.adaptee.subTitle()

    @subtitle.setter
    def subtitle(self, value):
        """ Invoked to set the sub-title. """

        self.adaptee.setSubTitle(value)

    @IWizardPage.title.getter
    def title(self):
        """ Invoked to get the title. """

        return self.adaptee.title()

    @title.setter
    def title(self, value):
        """ Invoked to set the title. """

        self.adaptee.setTitle(value)
