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


from ....model import adapt, observe
from ....pui import Dock
from ....ui import Application, IMainWindow

from ...i_action_hints import IActionHints
from ...i_area_hints import IAreaHints
from ...base_shell_adapter import BaseShellAdapter
from ...i_shell import IShell


@adapt(IMainWindow, to=IShell)
class IMainWindowIShellAdapter(BaseShellAdapter):
    """ Adapt IMainWindow to IShell. """

    @observe('views')
    def __views_changed(self, change):
        """ Invoked when the list of views changes. """

        main_window = IMainWindow(self.adaptee)
        stack = main_window.view

        # Remove any old views.
        for view in change.old:
            area_hints = IAreaHints(view)

            if area_hints.area == '':
                # Find the view in the stack.
                for stacked_view in stack.views:
                    if stacked_view is view:
                        stack.views.remove(stacked_view)
                        break
            else:
                # Find the dock.
                for dock in main_window.docks:
                    if dock.view is view:
                        main_window.docks.remove(dock)
                        break

        # Add any new views.
        for view in change.new:
            area_hints = IAreaHints(view)

            if area_hints.area in '':
                stack.views.append(view)
                stack.current_view = view
                Application().active_view = view
            else:
                dock = Dock()
                dock.view = view
                dock.title = view.title

                # Convert the shell area identifier to a main window dock area.
                dock_area = area_hints.area.split('.')[-1]
                dock.area = dock_area

                action_hints = IActionHints(view)
                dock.id = action_hints.id
                dock.within = action_hints.within

                main_window.docks.append(dock)
