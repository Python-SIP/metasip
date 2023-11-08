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


from .container_factory import ContainerFactory
from .i_grid import IGrid


class Grid(ContainerFactory):
    """ The Grid class arranges its contents in a grid. """

    # The interface that the view can be adapted to.
    interface = IGrid

    # The number of columns in the grid.
    nr_columns = IGrid.nr_columns

    # The number of rows in the grid.
    nr_rows = IGrid.nr_rows

    # The name of the toolkit factory method.
    toolkit_factory = 'grid'

    def initialise_view(self, view, model):
        """ Initialise the configuration of a view instance.

        :param view:
            is the view.
        :param model:
            is the model.
        """

        super().initialise_view(view, model)

        view.nr_columns = self.nr_columns
        view.nr_rows = self.nr_rows


# Register the view factory.
Grid.view_factories.append(Grid)
