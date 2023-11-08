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


from ..model import Interface


class ICloseViewVeto(Interface):
    """ The ICloseViewVeto interface defines the API to be implemented by a
    :term:`tool` that wants to exert control over whether or not a view can be
    closed.
    """

    def veto(self, view):
        """ Determine if the view is to be prevented from being closed.

        :param view:
            is the view.
        :return:
            ``True`` if the close of the view is to be prevented.
        """
