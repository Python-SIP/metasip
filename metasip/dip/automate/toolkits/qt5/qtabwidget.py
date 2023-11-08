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


from PyQt5.QtTest import QTest
from PyQt5.QtWidgets import QTabWidget

from ....automate import AutomationError, IAutomatedTabBar
from ....model import adapt, Adapter


@adapt(QTabWidget, to=IAutomatedTabBar)
class QTabWidgetIAutomatedTabBarAdapter(Adapter):
    """ An adapter to implement IAutomatedTabBar for a QTabWidget. """

    def simulate_select(self, id, delay, index):
        """ Simulate the user selecting a tab page.

        :param id:
            is the (possibly scoped) identifier of the widget.
        :param delay:
            is the delay in milliseconds between simulated events.
        :param index:
            is the index of the tab page.
        """

        tab_widget = self.adaptee

        if index < 0 or index >= tab_widget.count():
            raise AutomationError(id, 'select', "invalid index")

        if delay >= 0:
            QTest.qWait(delay)

        # This is the easiest way to make the page current.
        tab_widget.setCurrentIndex(index)
