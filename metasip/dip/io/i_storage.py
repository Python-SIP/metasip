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


from ..model import Instance, Interface, List

from .i_codec import ICodec
from .i_storage_ui import IStorageUi


class IStorage(Interface):
    """ The IStorage interface defines the API of a particular type of
    :term:`storage`.
    """

    # The codecs that can be used.
    codecs = List(ICodec)

    # The storage-specific user interfaces.
    ui = Instance(IStorageUi)

    # FIXME: Should have separate IStreamingStorage (with explicit_location())
    #        and IStructuredStorage (with implicit_location())?  Are the
    #        location factory methods needed at all?
    def explicit_location(self, location):
        """ If the storage has explicit storage locations (i.e. a location is
        independent on the value of a model) then convert such a location
        specified as a string to an :class:`~dip.io.IStorageLocation`
        instance.

        :param location:
            is the location as a string.  It should be valid for the storage.
        :return:
            the :class:`~dip.io.IStorageLocation` instance or ``None`` if the
            storage does not have explicit storage locations.
        """

    def implicit_location(self, model):
        """ If the storage has implicit storage locations (i.e. a location is
        dependent on the value of a model) then create such a location for the
        model.

        :param model:
            is the model.
        :return:
            the location or ``None`` if the storage does not have implicit
            storage locations.
        """

    def read(self, model, location):
        """ Read a model from a storage location.

        :param model:
            is the model.
        :param location:
            is the storage location where the model is read from.
        :return:
            the read model.  This may be the original model populated from the
            storage location, or it may be a different model (of an appropriate
            type) created from the storage location.  If ``None`` is returned
            then it is assumed that the read was abandoned and the user
            informed appropriately.
        """

    def readable_location(self, location):
        """ Convert a location specified as a string to a readable
        :class:`~dip.io.IStorageLocation` instance if possible.

        :param location:
            is the location as a string.
        :return:
            the :class:`~dip.io.IStorageLocation` instance or ``None`` if the
            location was not valid for this storage.
        """

    def write(self, model, location):
        """ Write a model to a storage location.

        :param model:
            is the model.
        :param location:
            is the storage location where the model is written to.
        """

    def writeable_location(self, location):
        """ Convert a location specified as a string to a writeable
        :class:`~dip.io.IStorageLocation` instance if possible.

        :param location:
            is the location as a string.
        :return:
            the :class:`~dip.io.IStorageLocation` instance or ``None`` if the
            location was not valid for this storage.
        """
