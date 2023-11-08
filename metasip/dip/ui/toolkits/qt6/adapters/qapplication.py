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


from PyQt6.QtWidgets import QApplication

from .....model import adapt, Adapter, notify_observers
from .....ui import IApplication, IContainer, IView

from ..utils import from_QWidget


@adapt(QApplication, to=IApplication)
class QApplicationIApplicationAdapter(Adapter):
    """ An adapter to implement IApplication for a QApplication. """

    def __init__(self):
        """ Initialise the adapter. """

        self.adaptee.focusChanged.connect(self._focus_changed)

        super().__init__()

    @IApplication.active_view.getter
    def active_view(self):
        """ Invoked to get the active view. """

        return _view_from_widget(self.adaptee.focusWidget())

    @active_view.setter
    def active_view(self, value):
        """ Invoked to set the active view. """

        if value is None:
            focus_widget = self.adaptee.focusWidget()

            if focus_widget is not None:
                focus_widget.clearFocus()
        else:
            IView(value).set_focus()

    def execute(self):
        """ Execute the application, i.e. enter its event loop.  It will return
        when the event loop terminates.

        :return:
            An integer exit code.
        """

        return self.adaptee.exec()

    def quit(self):
        """ Quit the application, i.e. force its event loop to terminate. """

        self.adaptee.quit()

    def _focus_changed(self, old_widget, new_widget):
        """ Invoked when the widget with the focus changes. """

        if old_widget is not new_widget:
            old_view = _view_from_widget(old_widget)
            new_view = _view_from_widget(new_widget)

            notify_observers('active_view', self, new_view, old_view)


def _view_from_widget(widget):
    """ Return the view corresponding to a focus widget. """

    if widget is None:
        view = None
    else:
        view = IView(widget, adapt=False, exception=False)
        if view is None:
            # Try and find the view in the widget hierachy.  If we don't find
            # anything then return the widget, even if it has never been
            # adapted to IView.  This means that in the case of a dip composite
            # view then the composite view will be returned rather than the
            # component widget.  It also means that the widget will be returned
            # if it was created independently of dip.
            parent = widget.parent()
            while parent is not None:
                # If the parent is a dip container then the widget was created
                # independently of dip.
                view = IContainer(widget, adapt=False, exception=False)
                if view is not None:
                    break

                view = IView(parent, adapt=False, exception=False)
                if view is not None:
                    break

                view = from_QWidget(parent)
                if view is not parent:
                    break

                parent = parent.parent()
            else:
                view = IView(widget)

    return view
