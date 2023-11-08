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


from PyQt6.QtWidgets import QLayout, QVBoxLayout, QWidget

from ....model import unadapted
from ....ui import IView


def as_QLayout(view):
    """ Return a view as a QLayout. """

    tk_view = unadapted(view)

    if isinstance(tk_view, QWidget):
        layout = _QWidgetShim()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(tk_view)

        tk_view = layout

    return tk_view


def from_QLayout(tk_view):
    """ Return a view from a QLayout. """

    if tk_view is None:
        return None

    if isinstance(tk_view, _QWidgetShim):
        tk_view = tk_view.itemAt(0).widget()

    return IView(tk_view)


class _QWidgetShim(QVBoxLayout):
    """ A shim for a QWidget when a QLayout is needed. """


def as_QWidget(view):
    """ Return a view as a QWidget. """

    tk_view = unadapted(view)

    if isinstance(tk_view, QLayout):
        # See if it already has a shim.
        widget = tk_view.parentWidget()

        if widget is None:
            widget = _QLayoutShim()
            widget.setLayout(tk_view)

        tk_view = widget

    return tk_view


def from_QWidget(tk_view):
    """ Return a view from a QWidget. """

    if tk_view is None:
        return None

    if isinstance(tk_view, _QLayoutShim):
        tk_view = tk_view.layout()

    return IView(tk_view)


class _QLayoutShim(QWidget):
    """ A shim for a QLayout when a QWidget is needed. """

    def closeEvent(self, event):
        """ Invoked when the widget wants to close. """

        tk_view = self.layout()

        for handler in IView(tk_view).close_request_handlers:
            if not handler(tk_view):
                event.ignore()
                break
        else:
            event.accept()


def as_QWidget_parent(view):
    """ Return a view as a QWidget in the object hierachy. """

    tk_view = unadapted(view)

    while tk_view is not None and not isinstance(tk_view, QWidget):
        tk_view = tk_view.parent()

    return tk_view
