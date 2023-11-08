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


from PyQt4.QtGui import QGroupBox

from .....model import adapt
from .....ui import IGroupBox

from .single_view_container_adapters import SingleViewContainerLayoutAdapter


@adapt(QGroupBox, to=IGroupBox)
class QGroupBoxIGroupBoxAdapter(SingleViewContainerLayoutAdapter):
    """ An adapter to implement IGroupBox for a QGroupBox. """

    @IGroupBox.title.getter
    def title(self):
        """ Invoked to get the title. """

        return self.adaptee.title()

    @title.setter
    def title(self, value):
        """ Invoked to set the title. """

        self.adaptee.setTitle(value)
