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


from PyQt5.QtWidgets import QSplitter

from .....model import adapt, Adapter
from .....ui import ISplitter

from ..utils import as_QWidget, from_QWidget

from .container_adapters import ContainerWidgetAdapter


@adapt(QSplitter, to=ISplitter)
class QSplitterISplitterAdapter(ContainerWidgetAdapter):
    """ An adapter to implement ISplitter for a QSplitter. """

    @ISplitter.views.getter
    def views(self):
        """ Invoked to get the views. """

        splitter = self.adaptee

        return tuple(from_QWidget(splitter.widget(idx))
                for idx in range(splitter.count()))

    @views.setter
    def views(self, value):
        """ Invoked to set the views. """

        splitter = self.adaptee

        # FIXME: Remove any existing widgets.
        for item in value:
            splitter.addWidget(as_QWidget(item))
