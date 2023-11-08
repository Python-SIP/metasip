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


from ..model import List

from .i_dialog import IDialog
from .single_subview_container_factory import SingleSubviewContainerFactory


class Dialog(SingleSubviewContainerFactory):
    """ The Dialog class implements a dialog factory, i.e. it creates views
    that implement the :class:`~dip.ui.IDialog` interface.
    """

    # The contents should always be automatically wrapped in a
    # :class:`~dip.ui.Form`.
    auto_form = 'always'

    # The dialog buttons.
    buttons = IDialog.buttons

    # The interface that the view can be adapted to.
    interface = IDialog

    # The name of the toolkit factory method.
    toolkit_factory = 'dialog'

    def initialise_view(self, view, model):
        """ Initialise the configuration of a view instance.

        :param view:
            is the view.
        :param model:
            is the model.
        """

        super().initialise_view(view, model)

        view.buttons = self.buttons

    @SingleSubviewContainerFactory.controller_factory.default
    def controller_factory(self):
        """ Invoked to return the default controller factory. """

        from .dialog_controller import DialogController

        return DialogController


# Register the view factory.
Dialog.view_factories.append(Dialog)
