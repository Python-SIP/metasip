# Copyright (c) 2017 Riverbank Computing Limited.
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
import urllib.parse

# FIXME: replace with proper toolkit support.
from .... import TOOLKIT
if TOOLKIT == 'qt4':
    from PyQt4.QtCore import QDir, QFile, QFileInfo
else:
    from PyQt5.QtCore import QDir, QFile, QFileInfo

from ....model import implements

from ... import IStorage

from .. import QIODeviceStorage


@implements(IStorage)
class FilesystemStorage(QIODeviceStorage):
    """ The FilesystemStorage class implements :term:`streaming storage` based
    on a local filesystem.
    """

    def explicit_location(self, location):
        """ Create a filesystem storage location from a string.

        :param location:
            is the location as a string.  It should be a valid filesystem name.
        :return:
            the storage location.
        """

        from .filesystem_storage_location import FilesystemStorageLocation

        # Convert to an absolute name using native separators.
        pathname = QFileInfo(location).absoluteFilePath()
        pathname = QDir.toNativeSeparators(pathname)

        return FilesystemStorageLocation(storage=self, pathname=pathname)

    def readable_location(self, location):
        """ Convert a location specified as a string to a readable
        :class:`~dip.io.IStorageLocation` instance if possible.

        :param location:
            is the location as a string.
        :return:
            the :class:`~dip.io.IStorageLocation` instance or ``None`` if the
            location was not valid for this storage.
        """

        location = self._valid_location(location)
        if location is None:
            return None

        if not os.path.exists(location):
            return None

        return self.explicit_location(location)

    def writeable_location(self, location):
        """ Convert a location specified as a string to a writeable
        :class:`~dip.io.IStorageLocation` instance if possible.

        :param location:
            is the location as a string.
        :return:
            the :class:`~dip.io.IStorageLocation` instance or ``None`` if the
            location was not valid for this storage.
        """

        location = self._valid_location(location)
        if location is None:
            return None

        return self.explicit_location(location)

    def qiodevice(self, location):
        """ A storage location is converted to a
        :class:`~PyQt4.QtCore.QIODevice` instance, specifically a
        :class:`~PyQt4.QtCore.QFile`.

        :param location:
            is the storage location.
        :return:
            the :class:`~PyQt4.QtCore.QFile`.
        """

        return QFile(location.pathname)

    @IStorage.ui.default
    def ui(self):
        """ Return the default implementation of the storage-specific user
        interfaces.
        """

        from .filesystem_storage_ui import FilesystemStorageUi

        return FilesystemStorageUi(storage=self)

    def _valid_location(self, location):
        """ Return a validated location. """

        # Handle the tivial case.
        if location == '':
            return None

        # If it has a drive then assume it is a filename.
        drive, _ = os.path.splitdrive(location)
        if drive != '':
            return location

        # If it doesn't have a URL schema then assume it is a filename.
        url = urllib.parse.urlparse(location)
        if url.scheme == '':
            return location

        return None
