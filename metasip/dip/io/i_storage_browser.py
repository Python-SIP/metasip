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


from ..model import Instance, Interface, Str

from .i_storage import IStorage
from .i_storage_location import IStorageLocation


class IStorageBrowser(Interface):
    """ The IStorageBrowser interface defines the API implemented by a view
    that allows the user to browse storage and select a valid
    :term:`storage location`.
    """

    # This explains why the storage location is invalid.  It will be an empty
    # string if the location is valid.
    invalid_reason = Str()

    # The storage location that the user uses the view to set.
    location = Instance(IStorageLocation)

    # The storage.
    storage = Instance(IStorage)
