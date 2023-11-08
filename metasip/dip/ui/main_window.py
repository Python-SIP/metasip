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


from ..model import Instance, List

from .action import Action
from .dock import Dock
from .i_main_window import IMainWindow
from .menu_bar import MenuBar
from .single_subview_container_factory import SingleSubviewContainerFactory


class MainWindow(SingleSubviewContainerFactory):
    """ The MainWindow class implements a main window factory, i.e. it creates
    views that implement the :class:`~dip.ui.IMainWindow` interface.
    """

    # The list of dock factories.
    docks = List(Dock)

    # The interface that the view can be adapted to.
    interface = IMainWindow

    # The factory for the menu bar.
    menu_bar = Instance(MenuBar)

    # The name of the toolkit factory method.
    toolkit_factory = 'main_window'

    def create_subviews(self, model, view, root):
        """ Create the sub-views for a containing view.

        :param model:
            is the model.
        :param view:
            is the containing view.
        :param root:
            is the optional root view.
        :return:
            the sub-views.
        """

        # Create any docks before any actions they define are referenced.
        for dock_factory in self.docks:
            dock = dock_factory.create_view(model, view, root)

            # Configure any action.
            action = dock.action
            if action is not None:
                root.actions.append(action)

            view.docks.append(dock)

        # Create any menu bar.
        if self.menu_bar is not None:
            view.menu_bar = self.menu_bar.create_view(model, view, root)

        return super().create_subviews(model, view, root)


# Register the view factory.
MainWindow.view_factories.append(MainWindow)
