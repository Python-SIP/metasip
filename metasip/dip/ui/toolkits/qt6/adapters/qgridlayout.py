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


from PyQt6.QtWidgets import QGridLayout, QLayout, QWidget

from .....model import adapt, unadapted
from .....ui import IGrid, IView

from .container_adapters import ContainerLayoutAdapter, ContainerWidgetAdapter


class GridAdapterMixin:
    """ A mixin for adapters implementing IGrid for widgets and layouts. """

    def tk_grid_nr_columns_getter(self, layout):
        """ Invoked to get the number of columns. """

        # Use the actual value if it appears valid.  Allow for the fact that
        # the column count is 1 even if the layout is empty.
        nr_columns = 0 if layout.count() == 0 else layout.columnCount()
        if nr_columns == 0:
            nr_columns = self._nr_columns

        return nr_columns

    def tk_grid_nr_rows_getter(self, layout):
        """ Invoked to get the number of rows. """

        # Use the actual value if it appears valid.  Allow for the fact that
        # the row count is 1 even if the layout is empty.
        nr_rows = 0 if layout.count() == 0 else layout.rowCount()
        if nr_rows == 0:
            nr_rows = self._nr_rows

        return nr_rows

    def tk_grid_views_getter(self, layout):
        """ Invoked to get the layout's views. """

        views = []
        holes = []
        for row in range(layout.rowCount()):
            for column in range(layout.columnCount()):
                itm = layout.itemAtPosition(row, column)
                if itm is None:
                    holes.append(None)
                    continue

                w = itm.widget()
                if w is not None:
                    views.extend(holes)
                    holes = []

                    views.append(IView(w))
                else:
                    l = itm.layout()
                    if l is not None:
                        views.extend(holes)
                        holes = []

                        views.append(IView(l))
                    else:
                        # Return None for empty cells but strip trailing ones.
                        holes.append(None)

        return tuple(views)

    def tk_grid_views_setter(self, layout, value):
        """ Invoked to set the layout's views. """

        # Get the dimensions before clearing the layout in case it is the
        # layout that is defining the size (e.g. when binding to a manually
        # created layout).
        nr_columns = self.nr_columns

        # Make sure we know the number of columns.
        if nr_columns <= 0:
            nr_rows = self.nr_rows

            if nr_rows <= 0:
                raise ValueError("unable to infer the dimensions of the grid")

            nr_columns = (len(value) + nr_rows - 1) // nr_rows

        # Clear the layout.
        while layout.count() > 0:
            layout.takeAt(0)

        # Populate the layout.
        row = 0
        column = 0
        for itm in value:
            itm = unadapted(itm)

            if isinstance(itm, QLayout):
                layout.addLayout(itm, row, column)
            elif isinstance(itm, QWidget):
                layout.addWidget(itm, row, column)

            column += 1
            if column == nr_columns:
                column = 0
                row += 1


@adapt(QGridLayout, to=IGrid)
class QGridLayoutIGridAdapter(ContainerLayoutAdapter, GridAdapterMixin):
    """ An adapter to implement IGrid for a QGridLayout. """

    @IGrid.nr_columns.getter
    def nr_columns(self):
        """ Invoked to get the number of columns. """

        return self.tk_grid_nr_columns_getter(self.adaptee)

    @IGrid.nr_rows.getter
    def nr_rows(self):
        """ Invoked to get the number of rows. """

        return self.tk_grid_nr_rows_getter(self.adaptee)

    @IGrid.views.getter
    def views(self):
        """ Invoked to get the view's sub-views. """

        return self.tk_grid_views_getter(self.adaptee)

    @views.setter
    def views(self, value):
        """ Invoked to set the view's sub-views. """

        self.tk_grid_views_setter(self.adaptee, value)
        self.tk_view_configure(value)


@adapt(QWidget, to=IGrid)
class QWidgetIGridAdapter(ContainerWidgetAdapter, GridAdapterMixin):
    """ An adapter to implement IGrid for a QWidget that wraps a QGridLayout.
    """

    @classmethod
    def isadaptable(cls, adaptee):
        """ Determine if this adapter can adapt a QWidget.

        :param adaptee:
            is the QWidget.
        :return:
            ``True`` if the QWidget can be adapted.
        """

        return isinstance(adaptee.layout(), QGridLayout)

    @IGrid.nr_columns.getter
    def nr_columns(self):
        """ Invoked to get the number of columns. """

        return self.tk_grid_nr_columns_getter(self.adaptee.layout())

    @IGrid.nr_rows.getter
    def nr_rows(self):
        """ Invoked to get the number of rows. """

        return self.tk_grid_nr_rows_getter(self.adaptee.layout())

    @IGrid.views.getter
    def views(self):
        """ Invoked to get the view's sub-views. """

        return self.tk_grid_views_getter(self.adaptee.layout())

    @views.setter
    def views(self, value):
        """ Invoked to set the view's sub-views. """

        self.tk_grid_views_setter(self.adaptee.layout(), value)
