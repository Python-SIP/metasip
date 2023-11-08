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


from ..model import Bool, Callable, Instance, List, Str, Trigger

from .i_object import IObject


class IView(IObject):
    """ The IView interface defines the API to be implemented (typically using
    adaptation) by a :term:`view`.
    """

    # The list of callables that will be called when the view makes a request
    # to be closed.  Each is called with the view as the only argument and must
    # return ``True`` for the close to proceed.
    close_request_handlers = List(Callable())

    # The controller.
    controller = Instance('.Controller')

    # This is set if the view is enabled.
    enabled = Bool(True)

    # The factory that created the view.
    factory = Instance('.ViewFactory')

    # This is triggered when the view is about to be made visible for the first
    # time.
    ready = Trigger()

    # The status tip.
    status_tip = Str()

    # The short, user friendly title of the view.  It may be used by different
    # views in different ways, for example a form may use it as a field label,
    # or a push button may use it as the text of the button.  If the view is a
    # top-level window then it is used as the window title and may include the
    # marker '[*]' which will be replaced by some, platform specific,
    # indication of the application's overall dirty state.
    title = Str()

    # The tool tip.
    tool_tip = Str()

    # This is set if the view is visible.
    visible = Bool(True)

    # The "What's This?" help.
    whats_this = Str()

    def all_views(self):
        """ Create a generator that will return this view and any views
        contained in it.

        :return:
            the generator.
        """

    def set_focus(self):
        """ Give the focus to the view. """
