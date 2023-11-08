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


from ..model import Bool, Interface


class IStorageFactory(Interface):
    """ The IStorageFactory interface defines the API of a factory for creating
    implementations of :class:`~dip.io.IStorage`.
    """

    # This is set if the storage is readable.
    readable = Bool(True)

    # This is set if the storage is writeable.
    writeable = Bool(True)

    def __call__(self, codecs):
        """ Create a storage instance.

        :param codecs:
            is the list of codecs that can be used by the storage.
        :return:
            the storage instance.
        """
