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


from PyQt4.QtGui import QToolButton

from .....model import adapt, notify_observers, unadapted
from .....ui import IToolButton

from .editor_adapters import EditorWidgetAdapter


@adapt(QToolButton, to=IToolButton)
class QToolButtonIToolButtonAdapter(EditorWidgetAdapter):
    """ An adapter to implement IToolButton for a QToolButton. """

    # The title is embedded.
    title_policy = 'embedded'

    def configure(self, properties):
        """ Configure the editor. """

        self.adaptee.clicked.connect(self._on_clicked)

        super().configure(properties)

    @IToolButton.action.getter
    def action(self):
        """ The getter for the button's action. """

        return self.adaptee.defaultAction()

    @action.setter
    def action(self, value):
        """ The setter for the button's action. """

        self.adaptee.setDefaultAction(unadapted(value))

    @IToolButton.value.getter
    def value(self):
        """ The getter for the editor's value. """

        # Any value will do as it is only used to pull the Trigger.
        return False

    @value.setter
    def value(self, value):
        """ The setter for the editor's value. """

        raise ValueError("cannot set the value of an IToolButton")

    def _on_clicked(self):
        """ Invoked when clicked. """

        notify_observers('value', self, True, False)
