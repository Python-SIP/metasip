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


from .container_factory import ContainerFactory
from .i_stack import IStack


class Stack(ContainerFactory):
    """ The Stack class arranges its contents as a stack where only one view is
    visible at a time.
    """

    # The interface that the view can be adapted to.
    interface = IStack

    # The visibilty of the tab bar.  'multiple' means that it is visible if the
    # stack contains more than one view.
    tab_bar = IStack.tab_bar

    # The name of the toolkit factory method.
    toolkit_factory = 'stack'

    def initialise_view(self, view, model):
        """ Initialise the configuration of a view instance.

        :param view:
            is the view.
        :param model:
            is the model.
        """

        super().initialise_view(view, model)

        view.tab_bar = self.tab_bar


# Register the view factory.
Stack.view_factories.append(Stack)
