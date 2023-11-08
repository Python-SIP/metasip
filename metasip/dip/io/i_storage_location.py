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

from .i_storage import IStorage


class IStorageLocation(Interface):
    """ The IStorageLocation interface defines the API of a
    :term:`storage location`.  Once created a storage location object will only
    ever refer to one specific location, i.e. a storage location object is
    never updated to refer to a different location.
    """

    # The storage that the location refers to.
    storage = Instance(IStorage)

    def __str__(self):
        """ Return a string representation of the location.  This must be able
        to be parsed by an implementation of
        :meth:`~dip.io.IStorage.valid_location`.

        :return:
            the string representation.
        """
