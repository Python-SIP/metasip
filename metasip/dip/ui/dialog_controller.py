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


from ..model import Instance, observe

from .controller import Controller
from .i_dialog import IDialog


class DialogController(Controller):
    """ The DialogController class is a :term:`controller` for handling
    dialogs.
    """

    # This determines if the controller should automatically update the model
    # when the user changes the value of an editor.
    auto_update_model = False

    # The view.
    view = Instance(IDialog)

    def update_view(self):
        """ Reimplemented to disable the accept button if the view is invalid.
        """

        self.view.acceptable = self.is_valid()

    @observe('view.accepted')
    def __on_accepted(self, change):
        """ Invoked when the dialog's accepted trigger is pulled. """

        # Update the model if not already done.
        if not self.auto_update_model:
            self.update_model()
