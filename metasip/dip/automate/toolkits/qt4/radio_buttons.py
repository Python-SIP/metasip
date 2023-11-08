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
from PyQt4.QtGui import QBoxLayout, QRadioButton, QWidget
from PyQt4.QtTest import QTest

from ....automate import IAutomatedEditor, AutomationError
from ....model import adapt, Adapter


class RadioButtonsAdapterMixin:
    """ A mixin for adapters implementing automation of widgets and layouts
    containing radion buttons.
    """

    @classmethod
    def tk_isadaptable(cls, layout):
        """ Determine if a layout contains at least one QRadioButton. """

        return isinstance(layout, QBoxLayout) and any(cls._tk_radio_buttons(layout))

    @classmethod
    def tk_simulate_set(cls, layout, id, delay, value):
        """ Simulate the user setting the editor value. """

        # Find the button to click.
        for button in cls._tk_radio_buttons(layout):
            if button.objectName() == value or button.text() == value:
                QTest.mouseClick(button, Qt.LeftButton, Qt.NoModifier,
                        QPoint(), delay)
                return

        raise AutomationError(id, 'set', "invalid value: {0}".format(value))

    @classmethod
    def _tk_radio_buttons(cls, layout):
        """ Return a generator for all the QRadioButtons in a layout. """

        for i in range(layout.count()):
            widget = layout.itemAt(i).widget()

            if isinstance(widget, QRadioButton):
                yield widget


@adapt(QBoxLayout, to=IAutomatedEditor)
class QBoxLayoutIAutomatedEditorAdapter(Adapter, RadioButtonsAdapterMixin):
    """ An adapter to implement IAutomatedEditor for a QBoxLayout containing
    radio buttons.
    """

    @classmethod
    def isadaptable(cls, adaptee):
        """ Determine if this adapter can adapt a QBoxLayout.

        :param adaptee:
            is the QBoxLayout.
        :return:
            ``True`` if the QBoxLayout can be adapted.
        """

        return cls.tk_isadaptable(adaptee)

    def simulate_set(self, id, delay, value):
        """ Simulate the user setting the editor value.

        :param id:
            is the (possibly scoped) identifier of the widget.
        :param delay:
            is the delay in milliseconds between simulated events.
        :param value:
            is the value to set.  The value is set for the QRadioButton whose
            objectName() or text() matches the value.
        """

        self.tk_simulate_set(self.adaptee, id, delay, value)


@adapt(QWidget, to=IAutomatedEditor)
class QWidgetIAutomatedEditorAdapter(Adapter, RadioButtonsAdapterMixin):
    """ An adapter to implement IAutomatedEditor for a QWidget containing
    radio buttons.
    """

    @classmethod
    def isadaptable(cls, adaptee):
        """ Determine if this adapter can adapt a QWidget.

        :param adaptee:
            is the QWidget.
        :return:
            ``True`` if the QWidget can be adapted.
        """

        layout = adaptee.layout()

        return layout is not None and cls.tk_isadaptable(layout)

    def simulate_set(self, id, delay, value):
        """ Simulate the user setting the editor value.

        :param id:
            is the (possibly scoped) identifier of the widget.
        :param delay:
            is the delay in milliseconds between simulated events.
        :param value:
            is the value to set.  The value is set for the QRadioButton whose
            objectName() or text() matches the value.
        """

        self.tk_simulate_set(self.adaptee.layout(), id, delay, value)
