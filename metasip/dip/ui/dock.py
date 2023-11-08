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


from .i_dock import IDock
from .single_subview_container_factory import SingleSubviewContainerFactory


class Dock(SingleSubviewContainerFactory):
    """ The Dock class implements a dock of a main window. """

    # The dock area that the dock is initially placed in.
    area = IDock.area

    # The interface that the view can be adapted to.
    interface = IDock

    # The name of the toolkit factory method.
    toolkit_factory = 'dock'

    # The identifier of an optional collection of actions that the action used
    # to toggle the dock visibility will be placed within.
    within = IDock.within

    def initialise_view(self, view, model):
        """ Initialise the configuration of a view instance.

        :param view:
            is the view.
        :param model:
            is the model.
        """

        super().initialise_view(view, model)

        view.area = self.area
        view.within = self.within


# Register the view factory.
Dock.view_factories.append(Dock)
