# Copyright (c) 2023 Riverbank Computing Limited.
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


from ..model import Interface, List, Str


class IQuitVeto(Interface):
    """ The IQuitVeto interface defines the API to be implemented by an object
    that is allowed to veto a user's request to quit the application.
    """

    # The list of separate reasons why the quit request should be vetoed.
    # Each reason must be a short, properly punctuated, one line sentence.  If
    # the list is empty then the request will not be vetoed.
    reasons = List(Str())
