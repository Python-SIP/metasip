# Copyright (c) 2023 Riverbank Computing Limited.
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


from PyQt6.QtWidgets import QDoubleSpinBox

from .....model import adapt
from .....ui import IFloatSpinBox

from .editor_adapters import EditorWidgetAdapter


@adapt(QDoubleSpinBox, to=IFloatSpinBox)
class QDoubleSpinBoxIFloatSpinBoxAdapter(EditorWidgetAdapter):
    """ An adapter to implement IFloatSpinBox for a QDoubleSpinBox. """

    def configure(self, properties):
        """ Configure the editor. """

        super().configure(properties)

        self.adaptee.valueChanged.connect(self.tk_editor_notify)

    @IFloatSpinBox.maximum.getter
    def maximum(self):
        """ Invoked to get the maximum value. """

        return self.adaptee.maximum()

    @maximum.setter
    def maximum(self, value):
        """ Invoked to set the maximum value. """

        widget = self.adaptee

        if value is None:
            # The Qt default.
            value = 99.99

        blocked = widget.blockSignals(True)
        widget.setMaximum(value)
        widget.blockSignals(blocked)

    @IFloatSpinBox.minimum.getter
    def minimum(self):
        """ Invoked to get the minimum value. """

        return self.adaptee.minimum()

    @minimum.setter
    def minimum(self, value):
        """ Invoked to set the minimum value. """

        widget = self.adaptee

        if value is None:
            # The Qt default.
            value = 0.0

        blocked = widget.blockSignals(True)
        widget.setMinimum(value)
        widget.blockSignals(blocked)

    @IFloatSpinBox.read_only.getter
    def read_only(self):
        """ Invoked to get the read-only state. """

        return self.adaptee.isReadOnly()

    @read_only.setter
    def read_only(self, value):
        """ Invoked to set the read-only state. """

        self.adaptee.setReadOnly(value)

    @IFloatSpinBox.value.getter
    def value(self):
        """ Invoked to get the editor's value. """

        return self.adaptee.value()

    @value.setter
    def value(self, value):
        """ Invoked to set the editor's value. """

        widget = self.adaptee

        # Save for the notifier.
        self.tk_editor_old_value = value

        blocked = widget.blockSignals(True)
        widget.setValue(value)
        widget.blockSignals(blocked)
