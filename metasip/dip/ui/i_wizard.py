# Copyright (c) 2011 Riverbank Computing Limited.
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


from ..model import Instance, Trigger, Tuple

from .i_container import IContainer
from .i_wizard_page import IWizardPage


class IWizard(IContainer):
    """ The IWizard interface defines the API to be implemented by a wizard.
    """

    # The current page.
    current_page = Instance(IWizardPage)

    # This is pulled when the user finishes the wizard.
    finished = Trigger()

    # The wizard's pages.
    views = Tuple(IWizardPage)

    def execute(self):
        """ Execute the wizard.

        :return:
            ``True`` if the user accepted the wizard.
        """
