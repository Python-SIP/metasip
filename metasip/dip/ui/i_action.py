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


from ..model import Bool, Callable, Instance, Model, Str, Trigger

from .i_object import IObject


class IAction(IObject):
    """ The IAction interface defines the API to be implemented by an
    :term:`action`.
    """

    # The name of the attribute in the model the action is bound to.  This is
    # not an :term:`attribute path`.
    attribute_name = Str()

    # This is set if the action is checkable.
    checkable = Bool()

    # This is set if the action is checked.
    checked = Bool(False)

    # This is set if the action is enabled.
    enabled = Bool()

    # The model containing the attribute the action is bound to.
    model = Instance(Model)

    # The plain text of the action.  This is the same as the text but with any
    # formatting hints (e.g. '&' or '...') removed.  It is typically used in
    # action specific dialog titles.
    plain_text = Str()

    # The shortcut.
    shortcut = Str()

    # The status tip.
    status_tip = Str()

    # The text of the action.
    text = Str()

    # The tool tip.
    tool_tip = Str()

    # This is set when the action is triggered.
    trigger = Trigger()

    # This is set if the widget is visible.
    visible = Bool()

    # The "What's This?" help.
    whats_this = Str()

    # This is called when the action is triggered.  It is passed the action as
    # its only argument.
    when_triggered = Callable()

    # The identifier of an optional collection of actions that this action will
    # be placed within.
    within = Str()
