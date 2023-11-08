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


from .....ui import ISingleViewContainer

from ..utils import as_QLayout, from_QLayout

from .container_adapters import ContainerWidgetAdapter


class SingleViewContainerWidgetAdapter(ContainerWidgetAdapter):
    """ The SingleViewContainerWidgetAdapter class is a base class for adapters
    than implement the :class:`~dip.pui.ISingleViewContainer` interface.
    """

    @ISingleViewContainer.views.getter
    def views(self):
        """ Invoked to get the views. """

        view = self.view

        return () if view is None else (view, )

    @views.setter
    def views(self, value):
        """ Invoked to set the views. """

        if len(value) > 1:
            raise ValueError("{0} can only contain a single view".format(
                    type(self.adaptee).__name__))

        self.view = value[0] if len(value) != 0 else None


class SingleViewContainerLayoutAdapter(SingleViewContainerWidgetAdapter):
    """ The SingleViewContainerLayoutAdapter class is a base class for adapters
    than implement the :class:`~dip.pui.ISingleViewContainer` interface and
    where the contained view is a :class:`~PyQt5.QtWidgets.QLayout`.
    """

    @ISingleViewContainer.view.getter
    def view(self):
        """ Invoked to get the contained view. """

        return from_QLayout(self.adaptee.layout())

    @view.setter
    def view(self, value):
        """ Invoked to set the contained view. """

        if value is not None:
            self.adaptee.setLayout(as_QLayout(value))
