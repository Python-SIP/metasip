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


from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow

from .....model import adapt, Adapter, observe, unadapted
from .....ui import IAction, IActionCollection, IMainWindow, IMenuBar

from ..exceptions import Qt5ToolkitError
from ..utils import as_QWidget, from_QWidget

from .single_view_container_adapters import SingleViewContainerWidgetAdapter


@adapt(QMainWindow, to=IMainWindow)
class QMainWindowIMainWindowAdapter(SingleViewContainerWidgetAdapter):
    """ An adapter to implement IMainWindow for a QMainWindow. """

    # Map toolkit independent dock areas to the Qt specific equivalents.
    _area_map = {
            'left': Qt.LeftDockWidgetArea,
            'right': Qt.RightDockWidgetArea,
            'top': Qt.TopDockWidgetArea,
            'bottom': Qt.BottomDockWidgetArea}

    def all_views(self):
        """ Create a generator that will return this view and any views
        contained in it.

        :return:
            the generator.
        """

        yield from super().all_views()

        for dock in self.docks:
            yield from dock.all_views()

    @observe('actions')
    def __actions_changed(self, change):
        """ Invoked when the list of actions changes. """

        qmenubar = self.adaptee.menuBar()

        if qmenubar is None:
            return

        # FIXME: Remove old actions.

        # Add any new actions.
        for action in change.new:
            if not IMenuBar(qmenubar).add_action(action):
                if isinstance(action, IAction):
                    raise Qt5ToolkitError(
                            "unable to position action '{0}'".format(
                                            IAction(action).id))

                raise Qt5ToolkitError(
                        "unable to position action collection '{0}'".format(
                                IActionCollection(action).id))

    @observe('docks')
    def __docks_changed(self, change):
        """ Invoked when the list of docks changes. """

        # FIXME: Remove old docks.

        # Add any new docks.
        for dock in change.new:
            # Convert the dock area.
            area = self._area_map[dock.area]

            # Add it to the main window.
            self.adaptee.addDockWidget(area, unadapted(dock))

            # Add any action.
            if dock.action is not None:
                dock.action.within = dock.within
                self.actions.append(dock.action)

    @IMainWindow.menu_bar.getter
    def menu_bar(self):
        """ Invoked to get the main window's menu bar. """

        return self.adaptee.menuBar()

    @menu_bar.setter
    def menu_bar(self, value):
        """ Invoked to set the main window's menu bar. """

        self.adaptee.setMenuBar(unadapted(value))

    @IMainWindow.view.getter
    def view(self):
        """ Invoked to get the main window's content. """

        return from_QWidget(self.adaptee.centralWidget())

    @view.setter
    def view(self, value):
        """ Invoked to set the main window's content. """

        self.adaptee.setCentralWidget(as_QWidget(value))
