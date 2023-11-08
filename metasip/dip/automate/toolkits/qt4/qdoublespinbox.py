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


from PyQt4.QtCore import Qt
from PyQt4.QtGui import QDoubleSpinBox
from PyQt4.QtTest import QTest

from ....automate import IAutomatedEditor
from ....model import adapt, Adapter


@adapt(QDoubleSpinBox, to=IAutomatedEditor)
class QDoubleSpinBoxIAutomatedEditorAdapter(Adapter):
    """ An adapter to implement IAutomatedEditor for the widget. """

    def simulate_set(self, id, delay, value):
        """ Simulate the user setting the editor value.

        :param id:
            is the (possibly scoped) identifier of the widget.
        :param delay:
            is the delay in milliseconds between simulated events.
        :param value:
            is the value to set.
        """

        widget = self.adaptee

        QTest.keyClicks(widget, "a", Qt.ControlModifier, delay)
        QTest.keyClicks(widget, str(value), Qt.NoModifier, delay)
