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


from ..model import Instance, Interface

from .i_view import IView


class IApplication(Interface):
    """ The IApplication interface defines the API to be implemented by an
    application created by :class:`~dip.ui.Application`.
    """

    # The active view (i.e. the one with the focus).
    active_view = Instance(IView)

    def execute(self):
        """ Execute the application, i.e. enter its event loop.  It will return
        when the event loop terminates.

        :return:
            An integer exit code.
        """

    def quit(self):
        """ Quit the application, i.e. force its event loop to terminate. """
