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


from ..model import Interface, Str, Subclass


# FIXME: Should ICode include IFilterHints?
class ICodec(Interface):
    """ The ICodec interface defines the API of codecs. """

    # The interface that a model must implement.  It is ``None`` if there is no
    # decoder.
    decoder_interface = Subclass(Interface)

    # The interface that a model must implement.  It is ``None`` if there is no
    # encoder.
    encoder_interface = Subclass(Interface)

    # The identifier of the format.
    format = Str()

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
            appropriate type) created from the storage location.  If ``None``
            is returned then it is assumed that the decoding was abandoned and
            the user informed appropriately.
        """

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
