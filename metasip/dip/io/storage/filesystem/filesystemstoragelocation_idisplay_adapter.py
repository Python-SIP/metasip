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


import os.path

from ....model import adapt, Adapter, DelegatedTo
from ....ui import IDisplay

from .filesystem_storage_location import FilesystemStorageLocation


@adapt(FilesystemStorageLocation, to=IDisplay)
class FilesystemStorageLocationIDisplayAdapter(Adapter):
    """ The FilesystemStorageLocationIDisplayAdapter adapts a
    :class:`~dip.io.storage.filesystem.FilesystemStorageLocation` to the
    :class:`~dip.ui.IDisplay` interface.
    """

    # The name.
    name = DelegatedTo('adaptee.pathname')

    @IDisplay.short_name.getter
    def short_name(self):
        """ Invoked to get the short name. """

        return os.path.basename(self.adaptee.pathname)
