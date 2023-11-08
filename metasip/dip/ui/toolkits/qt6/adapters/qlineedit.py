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


from PyQt6.QtWidgets import QLineEdit

from .....model import adapt
from .....ui import ILineEditor

from .editor_adapters import EditorWidgetAdapter


@adapt(QLineEdit, to=ILineEditor)
class QLineEditILineEditorAdapter(EditorWidgetAdapter):
    """ An adapter to implement ILineEditor for a QLineEdit. """

    def configure(self, properties):
        """ Configure the editor. """

        self.adaptee.textEdited.connect(self.tk_editor_notify)

        super().configure(properties)

    @ILineEditor.read_only.getter
    def read_only(self):
        """ Invoked to get the read-only status. """

        return self.adaptee.isReadOnly()

    @read_only.setter
    def read_only(self, value):
        """ Invoked to set the read-only status. """

        self.adaptee.setReadOnly(value)

    @ILineEditor.value.getter
    def value(self):
        """ Invoked to get the editor's value. """

        return self.adaptee.text()

    @value.setter
    def value(self, value):
        """ Invoked to set the editor's value. """

        # Save for the notifier.
        self.tk_editor_old_value = value

        # The value will be set after successful validation.  This has the
        # annoying side effect of moving the cursor to the end of the text.  As
        # a workaround we maintain the cursor position if it was not at the end
        # of the old text.
        old_len = len(self.adaptee.text())
        old_pos = self.adaptee.cursorPosition()

        self.adaptee.setText(value)

        if old_len > 0 and old_pos < old_len:
            self.adaptee.setCursorPosition(old_pos)
