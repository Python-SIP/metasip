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
from PyQt4.QtGui import QDialog, QDialogButtonBox
from PyQt4.QtTest import QTest

from ....automate import AutomationError, IAutomatedDialog
from ....model import adapt, Adapter


# The map of dip dialog buttons to the Qt equivalents.
_button_map = {'ok': QDialogButtonBox.Ok, 'cancel': QDialogButtonBox.Cancel,
        'yes': QDialogButtonBox.Yes, 'no': QDialogButtonBox.No}


@adapt(QDialog, to=IAutomatedDialog)
class QDialogIAutomatedDialogAdapter(Adapter):
    """ An adapter to implement IAutomatedDialog for the Qt dialog. """

    def simulate_click(self, id, delay, button):
        """ Simulate the user clicking a button.

        :param id:
            is the (possibly scoped) identifier of the widget.
        :param delay:
            is the delay in milliseconds between simulated events.
        :param button:
            is the button to click.
        """

        # Find the button widget in the button box.
        button_box = self.adaptee.findChild(QDialogButtonBox)

        if button_box is not None:
            button_widget = button_box.button(_button_map[button])
        else:
            button_widget = None

        if button_widget is None:
            raise AutomationError(id, 'click',
                    "no '{0}' button in dialog".format(button))

        QTest.mouseClick(button_widget, Qt.LeftButton, Qt.NoModifier, QPoint(),
                delay)
