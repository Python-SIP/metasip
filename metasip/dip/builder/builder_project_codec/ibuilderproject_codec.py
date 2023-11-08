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


from ...io import IFilterHints
from ...io.codecs.xml import XmlCodec, IXmlDecoder, IXmlEncoder
from ...model import adapt, Adapter

from .. import IBuilderProject


class IBuilderProjectCodec(XmlCodec):
    """ The IBuilderProjectCodec class implements an XML-based codec for models
    that implement the IBuilderProject interface.
    """

    # The identifier of the format.
    format = 'dip.builder.formats.project'

    @XmlCodec.decoder.default
    def decoder(self):
        """ Invoked to return the default decoder. """

        from .ibuilderproject_xml_decoder import IBuilderProjectXmlDecoder

        return IBuilderProjectXmlDecoder(format=self.format)

    @XmlCodec.encoder.default
    def encoder(self):
        """ Invoked to return the default encoder. """

        from .ibuilderproject_xml_encoder import IBuilderProjectXmlEncoder

        return IBuilderProjectXmlEncoder(format=self.format)


@adapt(IBuilderProject, to=[IFilterHints, IXmlDecoder, IXmlEncoder])
class IBuilderProjectCodecAdapter(Adapter):
    """ Adapt the IBuilderProject interface to the IFilterHints, IXmlDecoder
    and IXmlEncoder interfaces.
    """

    # The filter to use if the project is being stored in a file.
    filter = "DIP builder project files (*.dip)"
