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


from PyQt5.QtWidgets import QLayout, QWidget

from .....model import unadapted
from .....ui import IContainer, IView

from .view_adapters import ViewLayoutAdapter, ViewWidgetAdapter


class ContainerAdapterMixin:
    """ A mixin for adapters implementing IContainer for widgets and layouts.
    """

    def tk_container_all_views(self):
        """ Create a generator that will return this view and any views
        contained in it.

        :return:
            the generator.
        """

        yield self

        for view in self.views:
            yield from IView(view).all_views()

    def tk_container_views_getter(self, layout):
        """ Invoked to get a layout's views. """

        views = []
        for idx in range(layout.count()):
            itm = layout.itemAt(idx)

            w = itm.widget()
            if w is not None:
                views.append(IView(w))
            else:
                l = itm.layout()
                if l is not None:
                    views.append(IView(l))

        return tuple(views)

    def tk_container_views_setter(self, layout, value):
        """ Invoked to set a layout's views. """

        # Clear the layout.
        while layout.count() > 0:
            layout.takeAt(0)

        # Populate the layout.
        for itm in value:
            itm = unadapted(itm)

            if isinstance(itm, QLayout):
                layout.addLayout(itm)
            elif isinstance(itm, QWidget):
                layout.addWidget(itm)


class ContainerLayoutAdapter(ViewLayoutAdapter, ContainerAdapterMixin):
    """ The ContainerLayoutAdapter class is a base class for adapters that
    implement the remainder of the :class:`~dip.ui.IContainer` interface for Qt
    layouts.
    """

    def all_views(self):
        """ Create a generator that will return this view and any views
        contained in it.

        :return:
            the generator.
        """

        yield from self.tk_container_all_views()

    @IContainer.views.getter
    def views(self):
        """ Invoked to get the views's sub-views. """

        return self.tk_container_views_getter(self.adaptee)

    @views.setter
    def views(self, value):
        """ Invoked to set the views's sub-views. """

        self.tk_container_views_setter(self.adaptee, value)
        self.tk_view_configure(value)


class ContainerWidgetAdapter(ViewWidgetAdapter, ContainerAdapterMixin):
    """ The ContainerWidgetAdapter class is a base class for adapters than
    implement the remainder of the :class:`~dip.ui.IContainer` interface for Qt
    widgets.
    """

    def all_views(self):
        """ Create a generator that will return this view and any views
        contained in it.

        :return:
            the generator.
        """

        yield from self.tk_container_all_views()

    @IContainer.views.getter
    def views(self):
        """ Invoked to get the view's sub-views. """

        return self.tk_container_views_getter(self.adaptee.layout())

    @views.setter
    def views(self, value):
        """ Invoked to set the view's sub-views. """

        self.tk_container_views_setter(self.adaptee.layout(), value)
