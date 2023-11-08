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
from PyQt4.QtGui import QPushButton
from PyQt4.QtTest import QTest

from ....automate import IAutomatedTrigger
from ....model import adapt, Adapter


@adapt(QPushButton, to=IAutomatedTrigger)
class QPushButtonIAutomatedTriggerAdapter(Adapter):
    """ An adapter to implement IAutomatedTrigger for the widget. """

    def simulate_trigger(self, id, delay):
        """ Simulate the user pulling the trigger.

        :param id:
            is the (possibly scoped) identifier of the widget.
        :param delay:
            is the delay in milliseconds between simulated events.
        """

        QTest.mouseClick(self.adaptee, Qt.LeftButton, Qt.NoModifier, QPoint(),
                delay)
