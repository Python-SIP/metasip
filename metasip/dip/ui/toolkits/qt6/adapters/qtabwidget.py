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


from PyQt6.QtWidgets import QTabWidget

from .....model import adapt, notify_observers, observe
from .....ui import IStack

from ..utils import as_QWidget, from_QWidget

from .container_adapters import ContainerWidgetAdapter


@adapt(QTabWidget, to=IStack)
class QTabWidgetIStackAdapter(ContainerWidgetAdapter):
    """ An adapter to implement IStack for a QTabWidget. """

    def configure(self, properties):
        """ Configure the widget. """

        self.__tk_old_view = None

        self.adaptee.currentChanged.connect(self.__tk_on_current_changed)

        super().configure(properties)

    @IStack.current_view.getter
    def current_view(self):
        """ Invoked to get the current view. """

        widget = self.adaptee.currentWidget()

        if widget is None:
            return None

        for view in self.views:
            if as_QWidget(view.view) is widget:
                return view

        return None

    @current_view.setter
    def current_view(self, value):
        """ Invoked to set the current view. """

        for view in self.views:
            if view is value:
                self.adaptee.setCurrentWidget(as_QWidget(view))
                break

    @IStack.tab_bar.getter
    def tab_bar(self):
        """ Invoked to get the tab bars's visibility. """

        return self.adaptee.tabBar().isVisible()

    @tab_bar.setter
    def tab_bar(self, value):
        """ Invoked to set the tab bars's visibility. """

        if value == 'visible':
            visible = True
        elif value == 'hidden':
            visible = False
        else:
            visible = (self.adaptee.count() > 1)

        self.__tk_set_tab_bar_visible(visible)

    @IStack.views.getter
    def views(self):
        """ Invoked to get the view's sub-views. """

        qtabwidget = self.adaptee

        return [from_QWidget(qtabwidget.widget(i))
                for i in range(qtabwidget.count())]

    @observe('views')
    def __tk_on_views_changed(self, change):
        """ Invoked when the list of views changes. """

        qtabwidget = self.adaptee

        # Remove any old views.
        for view in change.old:
            for idx in range(qtabwidget.count()):
                if qtabwidget.widget(idx) is as_QWidget(view):
                    observe('title', view, self.__tk_on_view_title_changed,
                        remove=True)
                    qtabwidget.removeTab(idx)
                    break

        # Add any new views.  We need to take a copy of the shadow value as it
        # will get updated when __tk_on_current_changed() invokes the getter.
        all_views = list(self._views)

        for view in change.new:
            qtabwidget.insertTab(all_views.index(view), as_QWidget(view),
                    view.title)
            observe('title', view, self.__tk_on_view_title_changed)

        if self._tab_bar == 'multiple':
            self.__tk_set_tab_bar_visible(qtabwidget.count() > 1)

    def __tk_on_current_changed(self, idx):
        """ Invoked when the current view changes. """

        widget = self.adaptee.widget(idx)

        if widget is None:
            new_view = None
        else:
            for new_view in self.views:
                if as_QWidget(new_view) is widget:
                    break
            else:
                # This should never happen.
                return

            # Note that if we don't do this then (on macOS at least) when a tab
            # is closed the newly exposed tab doesn't get the focus.
            focus_widget = widget.focusWidget()
            if focus_widget is not None:
                focus_widget.setFocus()

        old_view = self.__tk_old_view
        self.__tk_old_view = new_view

        notify_observers('current_view', self, new_view, old_view)

    def __tk_on_view_title_changed(self, change):
        """ Invoked when the title of a view changes. """

        qtabwidget = self.adaptee

        qtabwidget.setTabText(qtabwidget.indexOf(as_QWidget(change.model)),
                change.new)

    def __tk_set_tab_bar_visible(self, visible):
        """ Set the visibility of the tab bar. """

        qtabwidget = self.adaptee

        qtabwidget.setDocumentMode(not visible)
        qtabwidget.tabBar().setVisible(visible)
