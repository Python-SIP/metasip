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


# FIXME: replace with proper toolkit support.
from PyQt6.QtCore import QIODevice

from ...model import Int

from .. import BaseStorage, StorageError


class QIODeviceStorage(BaseStorage):
    """ The QIODeviceStorage class is an abstract base class for storage that
    is accessed via a :class:`~PyQt6.QtCore.QIODevice`.
    """

    # The number of bytes to read at a time.
    read_buffer_size = Int(16384)

    def implicit_location(self, model):
        """ Return the implicit storage location for a model.

        :param model:
            is the model.
        :return:
            ``None`` as devices typically have explicit locations.
        """

        return None

    def read(self, model, location):
        """ Read a model from a filesystem location.

        :param model:
            is the model.
        :param location:
            is the filesystem location where the model is read from.
        :return:
            the read model.  This may be the original model populated
            from the filesystem location, or it may be a different model (of an
            appropriate type) created from the filesystem location.  If
            ``None`` is returned then it is assumed that the read was abandoned
            and the user informed appropriately.
        """

        device = self.qiodevice(location)

        if not device.open(QIODevice.OpenModeFlag.ReadOnly):
            raise StorageError(device.errorString(), location)

        def reader():
            while True:
                bytes = device.read(self.read_buffer_size)

                if bytes is None:
                    raise StorageError(device.errorString(), location)

                if len(bytes) == 0:
                    break

                yield bytes

        codec = self.decoder_for_model(model, location)
        model = codec.decode(model, reader(), location)

        device.close()

        return model

    def write(self, model, location):
        """ Write a model to a filesystem location.

        :param model:
            is the model.
        :param location:
            is the filesystem location where the model is written to.
        """

        device = self.qiodevice(location)

        if not device.open(QIODevice.OpenModeFlag.WriteOnly):
            raise StorageError(device.errorString(), location)

        codec = self.encoder_for_model(model, location)
        for bytes in codec.encode(model, location):
            if device.write(bytes) < 0:
                raise StorageError(device.errorString(), location)

        device.close()

    def qiodevice(self, location):
        """ A storage location is converted to a
        :class:`~PyQt4.QtCore.QIODevice` instance.  This must be reimplemented
        by a sub-class.

        :param location:
            is the storage location.
        :return:
            the :class:`~PyQt4.QtCore.QIODevice`.
        """
