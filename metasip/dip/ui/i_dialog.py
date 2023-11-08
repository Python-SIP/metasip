# Copyright (c) 2012 Riverbank Computing Limited.
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


from ..model import Bool, Enum, Trigger, Tuple

from .i_single_view_container import ISingleViewContainer


# The different dialog buttons.
DialogButton = Enum('ok', 'cancel', 'yes', 'no')


class IDialog(ISingleViewContainer):
    """ The IDialog interface defines the API to be implemented by a dialog.
    """

    # This is set, typically by a :term:`controller`, when the contents of the
    # dialog are acceptable.
    acceptable = Bool(True)

    # This is pulled when the user accepts the dialog.
    accepted = Trigger()

    # The dialog buttons.
    buttons = Tuple(DialogButton, default=('ok', 'cancel'))

    def execute(self):
        """ Execute the dialog as a modal dialog.

        :return:
            ``True`` if the user accepted the dialog.
        """
