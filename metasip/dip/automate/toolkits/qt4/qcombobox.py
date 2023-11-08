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
from PyQt4.QtGui import QComboBox
from PyQt4.QtTest import QTest

from ....automate import IAutomatedEditor, AutomationError
from ....model import adapt, Adapter, isadapted
from ....ui import IOptionSelector


@adapt(QComboBox, to=IAutomatedEditor)
class QComboBoxIAutomatedEditorAdapter(Adapter):
    """ An adapter to implement IAutomatedEditor for the widget. """

    def simulate_set(self, id, delay, value):
        """ Simulate the user setting the editor value.

        :param id:
            is the (possibly scoped) identifier of the widget.
        :param delay:
            is the delay in milliseconds between simulated events.
        :param value:
            is the value to set.  If the QComboBox implements IOptionSelector
            then the value must be valid for the options.  Otherwise the value
            must be either the integer index of the option or the text of the
            item.
        """

        widget = self.adaptee

        # FIXME: review to see if it can be removed (and so remove the dip.ui
        # import).
        if isadapted(widget, IOptionSelector):
            try:
                to_idx = IOptionSelector(widget).options.index(value)
            except ValueError:
                to_idx = -1
        elif isinstance(value, int):
            to_idx = value if value < widget.count() else -1
        else:
            to_idx = widget.findText(value)

        if to_idx < 0:
            raise AutomationError(id, 'set',
                    "invalid value: {0}".format(value))

        from_idx = widget.currentIndex()

        if from_idx < to_idx:
            for _ in range(from_idx, to_idx):
                QTest.keyClick(widget, Qt.Key_Down, Qt.NoModifier, delay)
        elif to_idx < from_idx:
            for _ in range(to_idx, from_idx):
                QTest.keyClick(widget, Qt.Key_Up, Qt.NoModifier, delay)
