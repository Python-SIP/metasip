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


from PyQt5.QtWidgets import QDockWidget

from .....model import adapt
from .....ui import IDock

from ..utils import as_QWidget, from_QWidget

from .single_view_container_adapters import SingleViewContainerWidgetAdapter


@adapt(QDockWidget, to=IDock)
class QDockWidgetIDockAdapter(SingleViewContainerWidgetAdapter):
    """ An adapter to implement IDock for a QDockWidget. """

    @IDock.action.default
    def action(self):
        """ Invoked to return the default action. """

        action = self.adaptee.toggleViewAction()

        # Configure the action.
        action.setObjectName(self.id)

        return action

    @IDock.view.getter
    def view(self):
        """ Invoked to get the contained view. """

        return from_QWidget(self.adaptee.widget())

    @view.setter
    def view(self, value):
        """ Invoked to set the contained view. """

        self.adaptee.setWidget(as_QWidget(value))
