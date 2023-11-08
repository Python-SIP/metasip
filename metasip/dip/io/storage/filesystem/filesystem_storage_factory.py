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


from ....model import implements, Model

from ... import IStreamingStorageFactory


@implements(IStreamingStorageFactory)
class FilesystemStorageFactory(Model):
    """ The FilesystemStorageFactory class is a factory for
    :term:`streaming storage` based on a local filesystem.
    """

    def __call__(self, codecs):
        """ Create a storage instance.

        :param codecs:
            is the list of codecs that can be used by the storage.
        :return:
            the storage instance.
        """

        from .filesystem_storage import FilesystemStorage

        return FilesystemStorage(codecs=codecs)
