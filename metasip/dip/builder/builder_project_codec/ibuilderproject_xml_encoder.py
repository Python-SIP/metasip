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


from ...io.codecs.xml import XmlEncoder


class IBuilderProjectXmlEncoder(XmlEncoder):
    """ The IBuilderProjectXmlEncoder class implements the encoding to XML of a
    builder project.
    """

    def encode_attribute(self, model, name, value, attribute_type, location, indent_level):
        """ A single attribute is encoded as an XML byte stream.

        :param model:
            is the model containing the attribute to encode.
        :param name:
            is the name of the attribute.  It may be '' if the value is a
            member of a container attribute.
        :param value:
            is the value of the attribute.
        :param attribute_type:
            is the type of the attribute.
        :param location:
            is the storage location where the encoded attribute will be
            written to.  It is mainly used for error reporting.
        :param indent_level:
            is the current indentation level as a number.
        :return:
            the next section of the encoded XML byte stream.
        """

        if name == 'distributions_defaults':
            # Encode the defaults as a model and remember the distribution
            # identifier.

            encoding = self.encoding
            indent = self.indentation(indent_level)

            for deflts in value:
                yield '{0}<defaults distribution="{1}">\n'.format(
                        indent, deflts.id).encode(encoding)

                for part in self.encode_model(deflts, location, indent_level + 1):
                    yield part

                yield '{0}</defaults>\n'.format(indent).encode(encoding)

        else:
            # All remaining attributes are encoded as normal.
            for part in super().encode_attribute(model, name, value, attribute_type, location, indent_level):
                yield part
