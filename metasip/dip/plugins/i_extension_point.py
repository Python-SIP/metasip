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


from ..model import Interface, List, Str


class IExtensionPoint(Interface):
    """ The IExtensionPoint interface defines the API of an
    :term:`extension point`.
    """

    # The list of contributions made.
    contributions = List()

    # The identifier of the extension point.
    id = Str()

    def bind(self, obj, name):
        """ Bind an attribute of an object to the extension point and update it
        with all contributions made so far.

        :param obj:
            is the object containing the attribute to bind to.
        :param name:
            is the name of the attribute to bind to.
        """

    def contribute(self, contribution):
        """ Contribute an object to all bound attributes.

        :param contribution:
            is the object to contribute.
        """
