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


from ..model import Instance, List, Str

from .action import Action
from .container_factory import ContainerFactory
from .i_menu import IMenu


class Menu(ContainerFactory):
    """ The Menu class implements a factory for menus that implement or can be
    adapted to :class:`~dip.ui.IMenu`.
    """

    # The contents of the view.
    contents = List(Instance('.Menu', '.Action', Str()))

    # The interface that the view can be adapted to.
    interface = IMenu

    # The name of the toolkit factory method.
    toolkit_factory = 'menu'

    # The visibility of the menu.  If this is None then the menu will be
    # visible only when it has some content.
    visible = IMenu.visible

    def create_subviews(self, model, view, root):
        """ Create the sub-views for a containing view.

        :param model:
            is the model.
        :param view:
            is the containing view.
        :param root:
            is the optional root view.
        :return:
            the sub-views.
        """

        subviews = []

        for content in self.contents:
            if isinstance(content, Menu):
                subview = content.create_view(model, view, root)
            elif isinstance(content, Action):
                subview = content(model)

                # Add actions to the root view's list.
                root.actions.append(subview)
            elif content == '':
                # The content is a separator.
                subview = content
            else:
                # Assume the content is the id of an existing action.
                for action in root.actions:
                    if action.id == content:
                        subview = action
                        break
                else:
                    # The content must be a placeholder for an action to be
                    # added later.
                    subview = content

            subviews.append(subview)

        return subviews


# Register the view factory.
Menu.view_factories.append(Menu)
