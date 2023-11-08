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


from ..model import Model

from .exceptions import StorageError


class BaseStorage(Model):
    """ The BaseStorage storage class is an optional base class for
    implementations of :class:`~dip.io.IStorage`.
    """

    def decoder_for_model(self, model, location):
        """ Returns one of the storage's codecs that can be used to decode a
        model.  An exception is raised if there is no suitable codec.

        :param model:
            is the model.
        :param location:
            is the location.  This is only used in exceptions.
        :return:
            the codec.
        """

        for codec in self.codecs:
            # Choose the first suitable one.
            if codec.decoder_interface(model, exception=False) is not None:
                return codec

        raise StorageError("no suitable decoder for {0}".format(model),
                location)

    def encoder_for_model(self, model, location):
        """ Returns one of the storage's codecs that can be used to encode a
        model.  An exception is raised if there is no suitable codec.

        :param model:
            is the model.
        :param location:
            is the location.  This is only used in exceptions.
        :return:
            the codec.
        """

        for codec in self.codecs:
            # Choose the first suitable one.
            if codec.encoder_interface(model, exception=False) is not None:
                return codec

        raise StorageError("no suitable encoder for {0}".format(model),
                location)
