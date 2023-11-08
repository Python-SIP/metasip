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


from PyQt6.QtWidgets import QLabel

from .....model import adapt
from .....ui import ILabel, IMessageArea

from .editor_adapters import EditorWidgetAdapter
from .view_adapters import ViewWidgetAdapter


@adapt(QLabel, to=ILabel)
class QLabelILabelAdapter(EditorWidgetAdapter):
    """ An adapter to implement ILabel for a QLabel. """

    @ILabel.value.getter
    def value(self):
        """ Invoked to get for the editor's value. """

        return self.adaptee.text()

    @ILabel.value.setter
    def value(self, value):
        """ Invoked to set for the editor's value. """

        self.adaptee.setText(value)


@adapt(QLabel, to=IMessageArea)
class QLabelIMessageAreaAdapter(ViewWidgetAdapter):
    """ An adapter to implement IMessageArea for a QLabel. """

    @IMessageArea.text.setter
    def text(self, value):
        """ The setter for the message area's text. """

        self.adaptee.setText(value)
