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


from ..model import Str

from .editor_factory import EditorFactory
from .i_tool_button import IToolButton


class ToolButton(EditorFactory):
    """ The ToolButton class implements a tool button editor factory for
    trigger attributes and actions.
    """

    # The id of the optional action that the editor will trigger.
    action = Str()

    # The interface that the view can be adapted to.
    interface = IToolButton

    # The name of the toolkit factory method.
    toolkit_factory = 'tool_button'

    def create_view(self, model, parent, root, top_level=False):
        """ Create a view instance.

        :param model:
            is the model.
        :param parent:
            is the optional parent view.
        :param root:
            is the optional root view.
        :param top_level:
            is ``True`` if the view is to be used as a top-level widget.
        :return:
            the view.
        """

        view = super().create_view(model, parent, root, top_level)

        if self.action != '':
            if self.bind_to != '':
                raise ValueError("an action cannot be specified if the tool button is bound to a model attribute")

            for act in root.actions:
                if act.id == self.action:
                    view.action = act
                    break
            else:
                raise ValueError(
                        "the view does not contain an action with id '{0}'".format(self.action))

        return view


# Register the view factory.
ToolButton.view_factories.append(ToolButton)
