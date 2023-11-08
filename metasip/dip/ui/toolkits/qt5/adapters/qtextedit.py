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


from PyQt5.QtWidgets import QTextEdit

from .....model import adapt
from .....ui import ITextEditor

from .editor_adapters import EditorWidgetAdapter


@adapt(QTextEdit, to=ITextEditor)
class QTextEditITextEditorAdapter(EditorWidgetAdapter):
    """ An adapter to implement ITextEditor for a QTextEdit. """

    def configure(self, properties):
        """ Configure the editor. """

        self.adaptee.textChanged.connect(self._on_text_changed)

        super().configure(properties)

    @ITextEditor.read_only.getter
    def read_only(self):
        """ Invoked to get the read-only state. """

        return self.adaptee.isReadOnly()

    @read_only.setter
    def read_only(self, value):
        """ Invoked to set the read-only state. """

        self.adaptee.setReadOnly(value)

    @ITextEditor.value.getter
    def value(self):
        """ Invoked to get the editor's value. """

        return self.adaptee.toPlainText()

    @value.setter
    def value(self, value):
        """ Invoked to set the editor's value. """

        widget = self.adaptee

        # Save for the notifier.
        self.tk_editor_old_value = value

        blocked = widget.blockSignals(True)
        widget.setPlainText(value)
        widget.blockSignals(blocked)

    def _on_text_changed(self):
        """ Invoked when the text changes. """

        self.tk_editor_notify(self.adaptee.toPlainText())
