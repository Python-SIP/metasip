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


from ..model import implements, Instance, Model, observe, Str, Tuple
from ..ui import IView

from .i_action_hints import IActionHints
from .i_area_hints import IAreaHints
from .i_tool import ITool


@implements(ITool)
class SimpleViewTool(Model):
    """ The SimpleViewTool class is a base class for shell tools implemented
    as a single view and that allows for the use of an action that toggles the
    visibility of the view.
    """

    # The identifier to use for any action.
    action_id = Str()

    # The identifier of the area where the view should be placed.
    area = Str('dip.shell.areas.left')

    # The tool's name.
    name = Str()

    # The view implementation.
    view = Instance(IView)

    # The tool's views.  Any initial views will be automatically added to the
    # shell.
    views = Tuple(IView)

    # The optional identifier of a collection of actions that any action will
    # be placed within.
    within = Str()

    @views.getter
    def views(self):
        """ Invoked to get the views. """

        view = self.view

        return () if view is None else (view, )

    @views.setter
    def views(self, value):
        """ Invoked to set the views. """

        if len(value) > 1:
            raise ValueError(
                    "{0} can only contain a single view".format(
                            type(self).__name__))

        self.view = value[0] if len(value) != 0 else None

    @observe('shell')
    def __shell_changed(self, change):
        """ Invoked when the shell changes. """

        # Make sure any view is configured.
        view = self.view

        if view is not None:
            IAreaHints(view).area = self.area
            view.title = self.name

            # Pass the action hints.
            action_hints = IActionHints(view)
            action_hints.id = self.action_id
            action_hints.within = self.within
