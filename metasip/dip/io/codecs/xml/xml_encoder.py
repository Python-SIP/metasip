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


import base64
import pickle

from ....model import (CollectionTypeFactory, Enum, get_model_types, Instance,
        Int, List, Model, Str, ValueTypeFactory)

from ... import FormatError


class XmlEncoder(Model):
    """ The XmlEncoder class implements a model encoder that encodes a
    :class:`~dip.model.Model` instance as XML.
    
    Note that, by default, pickle is used to encode any attributes that don't
    have a value corresponding to a fundamental Python type (i.e.
    :class:`~dip.model.Int`, :class:`~dip.model.List` etc.).  It is
    recommended (but not required) that the model is defined fully in terms of
    these fundamental types or that the encoder is sub-classed to handle
    attributes with non-fundamental types explicitly.
    """

    # The XML declaration.
    declaration = Str('<?xml version="1.0" encoding="UTF-8"?>')

    # The text to open the outermost element.
    document_start = Str()

    # The text to close the outermost element.
    document_end = Str('</DipModel>')

    # The encoding to use.
    encoding = Str('utf8')

    # The list of names of attributes to exclude.
    exclude = List(Str())

    # The identifier of the format.
    format = Str()

    # The list of names of attributes to include.  If this is empty then all
    # attributes are included unless they have been explicitly excluded.
    include = List(Str())

    # The number of spaces used for a single level of indentation.
    indentation_spaces = Int(2)

    def encode(self, model, location):
        """ A model is encoded as an XML byte stream.

        :param model:
            is the model to encode.
        :param location:
            is the storage location where the encoded model will be written to.
            It is mainly used for error reporting.
        :return:
            the next section of the encoded XML byte stream.
        """

        encoding = self.encoding

        yield '{0}\n'.format(self.declaration).encode(encoding)
        yield '{0}\n'.format(self.document_start).encode(encoding)

        for part in self.encode_model(model, location, 1):
            yield part

        yield '{0}\n'.format(self.document_end).encode(encoding)

    def encode_model(self, model, location, indent_level):
        """ A model is encoded as an XML byte stream.

        :param model:
            is the model to encode.
        :param location:
            is the storage location where the encoded model will be written
            to.  It is mainly used for error reporting.
        :param indent_level:
            is the current indentation level as a number.
        """

        for name, attribute_type in get_model_types(type(model)).items():
            if name in self.exclude:
                continue

            if len(self.include) > 0 and name not in self.include:
                continue

            if isinstance(attribute_type, ValueTypeFactory):
                value = getattr(model, name)

                for part in self.encode_attribute(model, name, value, attribute_type, location, indent_level):
                    yield part

    def encode_attribute(self, model, name, value, attribute_type, location, indent_level):
        """ A single attribute is encoded as an XML byte stream.

        :param model:
            is the model containing the attribute to encode.
        :param name:
            is the name of the attribute.  It may be '' if the value is a
            member of a collection attribute.
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

        encoding = self.encoding
        indent = self.indentation(indent_level)

        name_attr = ' name="{0}"'.format(name) if name != '' else ''

        element = attribute_type.__class__.__name__

        if value is None:
            yield '{0}<None{1}/>\n'.format(indent, name_attr).encode(encoding)

        elif isinstance(attribute_type, CollectionTypeFactory):
            try:
                handler = getattr(self, '_encode_' + element)
            except AttributeError:
                raise FormatError("Unknown element '{0}'".format(element),
                        location)

            yield '{0}<{1}{2}>\n'.format(indent, element, name_attr).encode(
                    encoding)

            for part in handler(model, value, attribute_type, location, indent_level + 1):
                yield part

            yield '{0}</{1}>\n'.format(indent, element).encode(encoding)

        elif isinstance(value, Model):
            # The value must be an item in a collection.
            yield '{0}<Instance{1}>\n'.format(indent, name_attr).encode(
                    encoding)

            # See if we know how to re-create it when decoding.
            if issubclass(attribute_type, Model):
                for part in self.encode_model(value, location, indent_level + 1):
                    yield part
            else:
                yield self._pickle_value(value, location, name) + b'\n'

            yield '{0}</Instance>\n'.format(indent).encode(encoding)

        else:
            # Try the basic types before resorting to pickle.  We don't use
            # model types because we want to encourage sub-classing them, but
            # we don't want to include knowledge of them in the XML.
            py_type = type(value)

            if py_type is bool:
                element = 'bool'
                value = str(value).encode(encoding)
            elif py_type is int:
                element = 'int'
                value = str(value).encode(encoding)
            elif py_type is float:
                element = 'float'
                value = str(value).encode(encoding)
            elif py_type is str:
                element = 'Enum' if isinstance(attribute_type, Enum) else 'str'
                value = self.escape(value).encode(encoding)
            else:
                element = 'pickle'
                value = self._pickle_value(value, location, name)

            yield '{0}<{1}{2}>'.format(indent, element, name_attr).encode(
                    encoding)
            yield value
            yield '</{0}>\n'.format(element).encode(encoding)

    def indentation(self, indent_level):
        """ Return a string that will indent a line to a particular level.

        :param indent_level:
            is the indentation level as a number.
        :return:
            the string.
        """

        return ' ' * (self.indentation_spaces * indent_level)

    @staticmethod
    def escape(value):
        """ Replace any characters with their corresponding entities.

        :param value:
            is the string to escape.
        :return:
            the escaped string.
        """

        value = value.replace('&', '&amp;')
        value = value.replace('"', '&quot;')
        value = value.replace("'", '&apos;')
        value = value.replace('<', '&lt;')
        value = value.replace('>', '&gt;')

        return value

    @document_start.default
    def document_start(self):
        """ Create the default document start. """

        return '<DipModel version="1" format="{0}">'.format(self.format)

    def _pickle_value(self, value, location, name=''):
        """ Return a pickled value. """

        try:
            # Hard code the default protocol for Python v2.6 in an attempt to
            # make the format portable.
            value = pickle.dumps(value, protocol=2)
        except pickle.PicklingError as e:
            if name == '':
                raise FormatError("Unable to pickle value: {0}".format(e),
                        location)
            else:
                raise FormatError(
                        "Unable to pickle '{0}' attribute: {1}".format(name,
                                e),
                        location)

        return base64.b64encode(value)

    def _encode_Dict(self, model, dict_value, dict_type, location, indent_level):
        """ Encode a dict. """

        for dict_elem_key, dict_elem_value in dict_value.items():
            for part in self.encode_attribute(model, '', dict_elem_key, dict_type.key_type, location, indent_level):
                yield part

            for part in self.encode_attribute(model, '', dict_elem_value, dict_type.value_type, location, indent_level):
                yield part

    def _encode_Instance(self, model, instance_value, instance_type, location, indent_level):
        """ Encode an instance. """

        # Try and encode it an attribute at a time if we will be able to
        # recreate it when decoding.
        if len(instance_type.types) == 1 and issubclass(instance_type.types[0], Model):
            for part in self.encode_model(instance_value, location, indent_level + 1):
                yield part
        else:
            yield self._pickle_value(instance_value, location) + b'\n'

    def _encode_List(self, model, list_value, list_type, location, indent_level):
        """ Encode a list. """

        for list_elem in list_value:
            for part in self.encode_attribute(model, '', list_elem, list_type.element_type, location, indent_level):
                yield part

    def _encode_Set(self, model, set_value, set_type, location, indent_level):
        """ Encode a set. """

        for set_elem in set_value:
            for part in self.encode_attribute(model, '', set_elem, set_type.element_type, location, indent_level):
                yield part

    def _encode_Tuple(self, model, tuple_value, tuple_type, location, indent_level):
        """ Encode a tuple. """

        for tuple_elem in tuple_value:
            for part in self.encode_attribute(model, '', tuple_elem, tuple_type.element_type, location, indent_level):
                yield part
