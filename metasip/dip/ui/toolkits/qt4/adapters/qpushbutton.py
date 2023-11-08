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


from PyQt4.QtGui import QPushButton

from .....model import adapt, notify_observers
from .....ui import IPushButton

from .editor_adapters import EditorWidgetAdapter


@adapt(QPushButton, to=IPushButton)
class QPushButtonIPushButtonAdapter(EditorWidgetAdapter):
    """ An adapter to implement IPushButton for a QPushButton. """

    # The title is embedded.
    title_policy = 'embedded'

    def configure(self, properties):
        """ Configure the editor. """

        self.adaptee.clicked.connect(self._on_clicked)

        super().configure(properties)

    @IPushButton.title.getter
    def title(self):
        """ Invoke to get the title. """

        return self.adaptee.text()

    @title.setter
    def title(self, value):
        """ Invoked to set the title. """

        self.adaptee.setText(value)

    @IPushButton.value.getter
    def value(self):
        """ Invoke to get the editor's value. """

        # Any value will do as it is only used to pull the Trigger.
        return True

    @value.setter
    def value(self, value):
        """ Invoked to set the editor's value. """

        raise ValueError("cannot set the value of an IPushButton")

    def _on_clicked(self):
        """ Invoked when clicked. """

        notify_observers('value', self, True, False)
