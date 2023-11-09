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


from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QCheckBox

from .....model import adapt
from .....ui import ICheckBox

from .editor_adapters import EditorWidgetAdapter


@adapt(QCheckBox, to=ICheckBox)
class QCheckBoxICheckBoxAdapter(EditorWidgetAdapter):
    """ An adapter to implement ICheckBox for a QCheckBox. """

    # The title policy.  The title is embedded but can be removed.
    title_policy = 'optional'

    def configure(self, properties):
        """ Configure the editor. """

        self.adaptee.stateChanged.connect(self._on_state_changed)

        super().configure(properties)

    def remove_title(self):
        """ Implement the 'optional' title policy. """

        self.adaptee.setText('')

    @ICheckBox.title.getter
    def title(self):
        """ Invoked to get the title. """

        return self.adaptee.text()

    @title.setter
    def title(self, value):
        """ Invoked to set the title. """

        self.adaptee.setText(value)

    @ICheckBox.value.getter
    def value(self):
        """ Invoked to get the editor's value. """

        return self.adaptee.checkState() is not Qt.CheckState.Unchecked

    @value.setter
    def value(self, value):
        """ Invoked to set the editor's value. """

        widget = self.adaptee

        # Save for the notifier.
        self.tk_editor_old_value = value

        blocked = widget.blockSignals(True)
        widget.setCheckState(
                Qt.CheckState.Checked if value else Qt.CheckState.Unchecked)
        widget.blockSignals(blocked)

    def _on_state_changed(self, state):
        """ Invoked when the state changes. """

        self.tk_editor_notify(state is not Qt.CheckState.Unchecked)
