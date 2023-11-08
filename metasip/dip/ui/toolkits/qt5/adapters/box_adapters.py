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
from .....ui import IBox, IView, Stretch

from .container_adapters import ContainerLayoutAdapter, ContainerWidgetAdapter


class BoxAdapterMixin:
    """ A mixin for adapters implementing IBox for widgets and layouts. """

    def tk_box_all_views(self, layout):
        """ Create a generator that will return this view and any views
        contained in it.
        """

        yield self

        for view in self.tk_box_views_getter(layout, include_stretch=False):
            yield from view.all_views()

    def tk_box_views_getter(self, layout, include_stretch=True):
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
                elif include_stretch:
                    s = itm.spacerItem()
                    if s is not None:
                        views.append(Stretch())

        return tuple(views)

    def tk_box_views_setter(self, layout, value):
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
            elif isinstance(itm, Stretch):
                layout.addStretch()


class BoxLayoutAdapter(ContainerLayoutAdapter, BoxAdapterMixin):
    """ The BoxLayoutAdapter class is a base class for adapters that adapt
    QBoxLayout instances to the IBox interface.
    """

    def all_views(self):
        """ Create a generator that will return this view and any views
        contained in it.

        :return:
            the generator.
        """

        yield from self.tk_box_all_views(self.adaptee)

    @IBox.views.getter
    def views(self):
        """ Invoked to get the views's sub-views. """

        return self.tk_box_views_getter(self.adaptee)

    @views.setter
    def views(self, value):
        """ Invoked to set the views's sub-views. """

        self.tk_box_views_setter(self.adaptee, value)
        self.tk_view_configure(value)


class BoxWidgetAdapter(ContainerWidgetAdapter, BoxAdapterMixin):
    """ The BoxWidgetAdapter class is a base class for adapters that adapt
    DHBoxWidget and DVBoxWidget instances to the IBox interface.
    """

    def all_views(self):
        """ Create a generator that will return this view and any views
        contained in it.

        :return:
            the generator.
        """

        yield from self.tk_box_all_views(self.adaptee.layout())

    @IBox.views.getter
    def views(self):
        """ Invoked to get the view's sub-views. """

        return self.tk_box_views_getter(self.adaptee.layout())

    @views.setter
    def views(self, value):
        """ Invoked to set the view's sub-views. """

        self.tk_box_views_setter(self.adaptee.layout(), value)
