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


from ...io import FormatError
from ...io.codecs.xml import XmlDecoder

from .. import DistributionManager


class IBuilderProjectXmlDecoder(XmlDecoder):
    """ The IBuilderProjectXmlDecoder class implements the decoding from XML of
    a builder project.
    """

    def decode_attribute(self, model, model_types, reader, source, location):
        """ Decode the current element as an attribute.

        :param model:
            is the model to populate from the decoded byte stream.
        :param model_types:
            is the dict of the model's types.
        :param reader:
            is the :class:`~PyQt5.QtCore.QXmlStreamReader` instance.
        :param source:
            is an iterator that will return the byte stream to be decoded.
        :param location:
            is the storage location where the encoded model is being read from.
            It is mainly used for error reporting.
        """

        # See if the element needs any special handling.
        if reader.name() == 'defaults':
            distribution_id = reader.attributes().value('distribution')
            if distribution_id == '':
                raise FormatError(
                        "Element 'defaults' has no 'distribution' attribute")

            distribution = DistributionManager.instance().distribution_manager.distribution(distribution_id)
            if distribution is None:
                # FIXME: Save the XML so that it can be written back later if
                # FIXME: needed.
                raise ValueError(
                        "unknown distribution '{0}'".format(distribution_id))

            defaults = distribution.defaults_factory()
            self.decode_model(defaults, reader, source, location)

            model.distributions_defaults.append(defaults)

        else:
            super().decode_attribute(model, model_types, reader, source,
                    location)
