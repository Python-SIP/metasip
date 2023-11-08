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


from ....model import Any, implements, Model

from ... import ICodec

from .i_xml_decoder import IXmlDecoder
from .i_xml_encoder import IXmlEncoder


@implements(ICodec)
class XmlCodec(Model):
    """ The XmlCodec class implements a codec that decodes and encodes
    instances of :class:`~dip.model.Model` as XML.  The codec does not set the
    :attr:`~dip.io.ICodec.format` attribute.  This should be defined in a
    sub-class or passed as an argument when the codec is created.
    """

    # The decoder itself.  It must have a ``decode`` method with the same
    # signature as the :class:`~dip.io.ICodec.decode` method.
    decoder = Any()

    # The decoder interface.
    decoder_interface = IXmlDecoder

    # The encoder itself.  It must have a ``decode`` method with the same
    # signature as the :class:`~dip.io.ICodec.encode` method.
    encoder = Any()

    # The encoder interface.
    encoder_interface = IXmlEncoder

    def decode(self, model, source, location):
        """ A model is decoded from a byte stream.

        :param model:
            is the model.
        :param source:
            is an iterator that will return the byte stream to be decoded.
        :param location:
            is the storage location where the encoded model is being read from.
            It is mainly used for error reporting.
        :return:
            the decoded model.  This may be the original model populated from
            the storage location, or it may be a different model (of an
            appropriate type) created from the storage location.
        """

        return self.decoder.decode(model, source, location)

    def encode(self, model, location):
        """ A model is encoded as a byte stream.

        :param model:
            is the model.
        :param location:
            is the storage location where the encoded model will be written to.
            It is mainly used for error reporting.
        :return:
            a generator that will return sections of the encoded byte stream.
        """

        return self.encoder.encode(model, location)

    @decoder.default
    def decoder(self):
        """ Invoked to return the default decoder. """

        from .xml_decoder import XmlDecoder

        return XmlDecoder(format=self.format)

    @encoder.default
    def encoder(self):
        """ Invoked to return the default encoder. """

        from .xml_encoder import XmlEncoder

        return XmlEncoder(format=self.format)
