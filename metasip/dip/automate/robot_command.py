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


# FIXME: replace with proper toolkit support.
from .. import TOOLKIT
if TOOLKIT == 'qt4':
    from PyQt4.QtGui import QApplication, QLayout, QMenuBar, QWidget
    from PyQt4.QtTest import QTest
else:
    from PyQt5.QtTest import QTest
    from PyQt5.QtWidgets import QApplication, QLayout, QMenuBar, QWidget

from ..model import Dict, Int, Model, Str, Tuple

from .i_automated import IAutomated
from .exceptions import AutomationError


# The period in milliseconds between checking to see if a widget is visible.
POLL_PERIOD = 200


class RobotCommand(Model):
    """ The RobotCommand class encapsulates the information needed to execute
    an automation command.
    """

    # The delay in milliseconds between simulated events.
    delay = Int()

    # The name of the command.
    command = Str()

    # The positional arguments to the command.
    command_args = Tuple()

    # The keyword arguments to the command.
    command_kwargs = Dict()

    # The time in milliseconds to wait for the user interface widget to be
    # visible.  A negative value means that the widget should already be
    # visible.
    timeout = Int(-1)

    # The, possibly scoped, identifier of the user interface widget to apply
    # the command to.  Normally a simple identifier is sufficient to specify
    # the widget but the identifiers of containing widgets may be specified to
    # define the scope within which the rest of the identifier is limited to.
    # The scopes are separated by a ``:``.  For example if there is a widget
    # with the identifier ``a.b`` that contains two widgets with identifiers
    # ``x`` and ``y``, and there is another widget with the identifier ``c.d``
    # which contains a widget with the identifier ``x``, then the two ``x``
    # widgets should be referenced as ``a.b:x`` and ``c.d:x`` but the ``y``
    # widget can be referenced simply as ``y``.  Using scopes has the
    # disadvantage that they reflect the GUI layout and if the layout were to
    # change then the reference (and any automation scripts using it) would
    # need to be changed.  A better alternative would be to ensure that widgets
    # had different identifiers.
    id = Str()

    def __call__(self):
        """ Execute the command. """

        # Find the automated item.
        id_scope = self.id.split(':')
        timeout = self.timeout

        # Give the GUI time to be created.
        item = self._find_automated_item(id_scope)
        while item is None:
            if timeout < 0:
                raise AutomationError(self.id, self.command,
                        "no such automated item is visible")

            QTest.qWait(POLL_PERIOD)
            timeout -= POLL_PERIOD

            item = self._find_automated_item(id_scope)

        # Get the simulator methods from the item.
        simulate = getattr(IAutomated(item), 'simulate_' + self.command, None)
        if simulate is None:
            raise AutomationError(self.id, self.command, "unsupported command")

        # Execute the command.
        simulate(self.id, self.delay, *self.command_args,
                **self.command_kwargs)

    def _find_automated_item(self, id_scope, root=None):
        """ Return the item at the given scope relative to the root that
        implements the IAutomated interface.
        """

        # We need an item that implements IAutomated unless we are descoping.
        need_automated = (len(id_scope) == 1)

        id = id_scope[0]

        # Find the visible widgets that correspond to the head of the scope.
        if root is None:
            items = []
            for tlw in QApplication.topLevelWidgets():
                if tlw.objectName() == id:
                    items.append(tlw)

                items.extend(
                        tlw.findChildren((QLayout, QWidget), id))
        elif isinstance(root, QLayout):
            items = self._find_in_layout(root, id)
        elif isinstance(root, QWidget):
            items = root.findChildren((QLayout, QWidget), id)
        else:
            items = [root]

        item = None
        for itm in items:
            # Check that the item is visible.
            if isinstance(itm, QMenuBar) and itm.isNativeMenuBar():
                # Qt doesn't provide the correct visibility for native menu
                # bars so we assume it is visible.
                pass
            elif isinstance(itm, QWidget):
                if not itm.isVisible():
                    continue
            elif isinstance(itm, QLayout):
                if not itm.parentWidget().isVisible():
                    continue

            if need_automated:
                automated = IAutomated(itm, exception=False)
                if automated is None:
                    continue

            if item is not None:
                raise AutomationError(self.id, self.command,
                        "'{0}' identifies more than one item".format(
                                id_scope[0]))

            item = itm

        # All done if we have found nothing or we have used up the scope.
        if item is None or need_automated:
            return item

        return self._find_automated_item(id_scope[1:], item)

    def _find_in_layout(self, layout, id):
        """ Return all layouts and widgets managed by a layout. """

        items = []
        for idx in range(layout.count()):
            itm = layout.itemAt(idx)

            w = itm.widget()
            if w is not None:
                if w.objectName() == id:
                    items.append(w)

                items.extend(w.findChildren((QLayout, QWidget), id))
            else:
                l = itm.layout()
                if l is not None:
                    if l.objectName() == id:
                        items.append(l)

                    items.extend(self._find_in_layout(l, id))

        return items
