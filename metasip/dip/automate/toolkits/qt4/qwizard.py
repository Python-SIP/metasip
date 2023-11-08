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


from PyQt4.QtCore import QPoint, Qt
from PyQt4.QtGui import QWizard
from PyQt4.QtTest import QTest

from ....automate import AutomationError, IAutomatedDialog
from ....model import adapt, Adapter


@adapt(QWizard, to=IAutomatedDialog)
class QWizardIAutomatedDialogAdapter(Adapter):
    """ An adapter to implement IAutomatedDialog for the Qt dialog. """

    def simulate_click(self, id, delay, button):
        """ Simulate the user clicking a button.

        :param id:
            is the (possibly scoped) identifier of the widget.
        :param delay:
            is the delay in milliseconds between simulated events.
        :param button:
            is the :class:`~PyQt4.QtWidgets.QWizard.WizardButton` to click.
        """

        # Find the button widget.
        # FIXME: Use an abstract button name instead.
        button_widget = self.adaptee.button(button)

        if button_widget is None:
            raise AutomationError(id, 'click',
                    "no {0} button in wizard".format(hex(button)))

        QTest.mouseClick(button_widget, Qt.LeftButton, Qt.NoModifier, QPoint(),
                delay)
