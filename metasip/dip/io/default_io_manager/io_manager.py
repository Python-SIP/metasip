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


from ...model import implements, Model

from .. import ICodec, IIoManager, StorageError


@implements(IIoManager)
class IoManager(Model):
    """ The IoManager class is the default implementation of the
    :class:`~dip.io.IIoManager` interface.
    """

    def read(self, model, location, format):
        """ Read a model from a location using a particular format.

        :param model:
            is the model.
        :param location:
            is the location as a string.  This should identify a valid and
            unambiguous storage location.
        :param format:
            is the format.
        :return:
            the read model.  This may be the original model populated from the
            storage location, or it may be a different model (of an appropriate
            type) created from the storage location.  If ``None`` is returned
            then it is assumed that the read was abandoned and the user
            informed appropriately.
        """

        locations = self.readable_locations_from_string(location, format)

        if len(locations) != 1:
            raise StorageError("unknown or ambiguous location", location)

        location = locations[0]

        return location.storage.read(model, location)

    def readable_locations_from_string(self, location, format=''):
        """ Get the list of readable storage location instances for which a
        location specified as a string is valid.

        :param location:
            is the location as a string.
        :param format:
            is the identifier of the optional format.
        :return:
            the list of storage location instances.
        """

        locations = []
        for storage in self.readable_storage(format):
            storage_location = storage.readable_location(location)
            if storage_location is not None:
                locations.append(storage_location)

        return locations

    def readable_storage(self, format=''):
        """ Get the list of the storage instances that can be read from using a
        particular format.

        :param format:
            is the identifier of the optional format.
        :return:
            the list of storage instances.
        """

        if format != '':
            return self._storage_for_format(format, reading=True)

        storage_list = []

        for storage_factory in self.storage_factories:
            if storage_factory.readable:
                storage_list.append(storage_factory(codecs=[]))

        return storage_list

    def write(self, model, location, format):
        """ Write a model to a location using a particular format.

        :param model:
            is the model.
        :param location:
            is the location as a string.  This should identify a valid and
            unambiguous storage location.
        :param format:
            is the format.
        """

        locations = self.writeable_locations_from_string(location, format)

        if len(locations) != 1:
            raise StorageError("unknown or ambiguous location", location)

        location = locations[0]

        location.storage.write(model, location)

    def writeable_locations_from_string(self, location, format=''):
        """ Get the list of writeable storage location instances for which a
        location specified as a string is valid.

        :param location:
            is the location as a string.
        :param format:
            is the identifier of the optional format.
        :return:
            the list of storage location instances.
        """

        locations = []
        for storage in self.writeable_storage(format):
            storage_location = storage.writeable_location(location)
            if storage_location is not None:
                locations.append(storage_location)

        return locations

    def writeable_storage(self, format=''):
        """ Get the list of the storage instances that can be written to using
        a particular format.

        :param format:
            is the identifier of the optional format.
        :return:
            the list of storage instances.
        """

        if format != '':
            return self._storage_for_format(format, reading=False)

        storage_list = []

        for storage_factory in self.storage_factories:
            if storage_factory.writeable:
                storage_list.append(storage_factory(codecs=[]))

        return storage_list

    @IIoManager.ui.default
    def ui(self):
        """ Return the default implementation of the storage-independent user
        interfaces.
        """

        from .io_manager_ui import IoManagerUi

        return IoManagerUi(io_manager=self)

    def _storage_for_format(self, format, reading):
        """ Return a list of storage instances that can handle a format. """

        storage_list = []

        streaming_codecs = []
        for codec in self.codecs:
            if self._invalid_codec(codec, format, reading):
                continue

            streaming_codecs.append(codec)

        for storage_factory in self.storage_factories:
            usable = storage_factory.readable if reading else storage_factory.writeable
            if not usable:
                continue

            if isinstance(storage_factory, ICodec):
                if self._invalid_codec(storage_factory, format, reading):
                    continue

                codecs = [storage_factory]
            elif len(streaming_codecs) == 0:
                continue
            else:
                codecs = streaming_codecs

            # Create the storage instance bound to the codecs.
            storage = storage_factory(codecs)

            # Apply any storage policies.
            for storage_policy in self.storage_policies:
                if not storage_policy(format, storage):
                    break
            else:
                storage_list.append(storage)

        return storage_list

    @staticmethod
    def _invalid_codec(codec, format, reading):
        """ Check the validity of a codec. """

        if codec.format != format:
            return True

        iface = codec.decoder_interface if reading else codec.encoder_interface

        return iface is None
