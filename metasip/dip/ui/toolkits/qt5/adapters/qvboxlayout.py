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


from PyQt5.QtWidgets import QVBoxLayout, QWidget

from .....model import adapt
from .....ui import IVBox

from .box_adapters import BoxLayoutAdapter, BoxWidgetAdapter


@adapt(QVBoxLayout, to=IVBox)
class QVBoxLayoutIVBoxAdapter(BoxLayoutAdapter):
    """ An adapter to implement IVBox for a QVBoxLayout. """


@adapt(QWidget, to=IVBox)
class QWidgetIVBoxAdapter(BoxWidgetAdapter):
    """ An adapter to implement IVBox for a QWidget that wraps a QVBoxLayout.
    """

    @classmethod
    def isadaptable(cls, adaptee):
        """ Determine if this adapter can adapt a QWidget.

        :param adaptee:
            is the QWidget.
        :return:
            ``True`` if the QWidget can be adapted.
        """

        return isinstance(adaptee.layout(), QVBoxLayout)
