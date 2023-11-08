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
from PyQt4.QtGui import QListView
from PyQt4.QtTest import QTest

from ....automate import AutomationError, IAutomatedOptionSelector
from ....model import adapt, Adapter


@adapt(QListView, to=IAutomatedOptionSelector)
class QListViewIAutomatedOptionSelectorAdapter(Adapter):
    """ An adapter to implement IAutomatedOptionSelector for a QListView. """

    def simulate_select(self, id, delay, value):
        """ Simulate the user selecting an option.

        :param id:
            is the (possibly scoped) identifier of the widget.
        :param delay:
            is the delay in milliseconds between simulated events.
        :param value:
            is the value of the option.
        """

        list_view = self.adaptee
        model = list_view.model()

        if value is None:
            itm = None
        else:
            # Find the item that has the option as the UserRole (if there is
            # one) or the displayed text (for non-dip widgets being automated).
            for row_nr in range(model.rowCount()):
                itm = model.item(row_nr)

                if itm.data(Qt.UserRole) == value:
                    break

                if itm.text() == value:
                    break
            else:
                raise AutomationError(id, 'select', "invalid option")

        if delay >= 0:
            QTest.qWait(delay)

        if itm is None:
            list_view.selectionModel().clear()
        else:
            list_view.setCurrentIndex(model.indexFromItem(itm))
