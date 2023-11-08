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


import base64
import pickle

from PyQt6.QtCore import QXmlStreamReader

from ....model import (Any, Bool, Dict, Enum, Float, get_model_types, Instance,
        Int, List, Model, Set, Str, Tuple)

from ... import FormatError


class XmlDecoder(Model):
    """ The XmlDecoder class implements a model decoder that decodes a
    :class:`~dip.model.Model` instance from XML.
    """

    # The identifier of the format.
    format = Str()

    def decode(self, model, source, location):
        """ A model is decoded from an XML byte stream.

        :param model:
            is the model to populate from the decoded byte stream.
        :param source:
            is an iterator that will return the byte stream to be decoded.
        :param location:
            is the storage location where the encoded model is being read from.
            It is mainly used for error reporting.
        :return:
            the decoded model.
        """

        reader = QXmlStreamReader()

        if not self._next_element(reader, source, location):
            raise FormatError("The XML file is empty", location)

        self.decode_document_element(model, reader, location)

        self.decode_model(model, reader, source, location)

        return model

    def decode_document_element(self, model, reader, location):
        """ Decode the document element (i.e. the outermost element).

        :param model:
            is the model to populate from the decoded byte stream.
        :param reader:
            is the :class:`~PyQt6.QtCore.QXmlStreamReader` instance.
        :param location:
            is the storage location where the encoded model is being read from.
            It is mainly used for error reporting.
        """

        if reader.name() != 'DipModel':
            raise FormatError(
                    "'DipModel' element expected, not '{0}'".format(
                            reader.name()),
                    location)

        attributes = reader.attributes()

        version = attributes.value('version')
        if version != '1':
            raise FormatError(
                    "Version '1' expected, not '{0}'".format(version),
                    location)

        format = attributes.value('format')
        if format != self.format:
            raise FormatError(
                    "Format '{0}' expected, not '{1}'".format(self.format,
                            format),
                    location)

    def decode_model(self, model, reader, source, location):
        """ Decode the next element as a model.

        :param model:
            is the model to populate from the decoded byte stream.
        :param reader:
            is the :class:`~PyQt6.QtCore.QXmlStreamReader` instance.
        :param source:
            is an iterator that will return the byte stream to be decoded.
        :param location:
            is the storage location where the encoded model is being read
            from.  It is mainly used for error reporting.
        """

        model_types = get_model_types(type(model))

        while self._next_element(reader, source, location):
            self.decode_attribute(model, model_types, reader, source, location)

    def decode_attribute(self, model, model_types, reader, source, location):
        """ Decode the current element as an attribute.

        :param model:
            is the model to populate from the decoded byte stream.
        :param model_types:
            is the dict of the model's types.
        :param reader:
            is the :class:`~PyQt6.QtCore.QXmlStreamReader` instance.
        :param source:
            is an iterator that will return the byte stream to be decoded.
        :param location:
            is the storage location where the encoded model is being read from.
            It is mainly used for error reporting.
        """

        name = reader.name()

        # Make sure there was a name.
        attributes = reader.attributes()
        aname = attributes.value('name')

        if aname == '':
            raise FormatError(
                    "Element '{0}' has no 'name' attribute".format(name),
                    location)

        # Get the attribute type.
        try:
            atype = model_types[aname]
        except KeyError:
            raise FormatError(
                    "'{0}' type has no '{1}' attribute".format(
                            type(model).__name__, aname),
                    location)

        # Convert the value.
        value = self._decode_element(name, aname, atype, reader, source,
                location)

        # Set the value.
        setattr(model, aname, value)

    def _decode_element(self, name, aname, atype, reader, source, location):
        """ Decode the current element and return the value. """

        try:
            handler = getattr(self, '_decode_' + name)
        except AttributeError:
            raise FormatError("{0}: unknown element '{1}'".format(aname, name),
                    location)

        return handler(aname, atype, reader, source, location)

    def _decode_bool(self, aname, atype, reader, source, location):
        """ Decode to a bool. """

        self._check_model_type(aname, atype, Bool, location)

        value = reader.readElementText()

        if value == 'True':
            value = True
        elif value == 'False':
            value = False
        else:
            raise FormatError(
                    "{0}: unable to convert value from '{1}' to a bool".format(
                            aname, value),
                    location)

        return value

    def _decode_Dict(self, aname, atype, reader, source, location):
        """ Decode to a dict. """

        self._check_model_type(aname, atype, Dict, location)

        value = {}

        while self._next_element(reader, source, location):
            item_key = self._decode_element(reader.name(), aname,
                    atype.key_type, reader, source, location)

            if not self._next_element(reader, source, location):
                raise FormatError(
                        "{0}: dict has key but no corresponding value".format(
                                aname),
                        location)

            item_value = self._decode_element(reader.name(), aname,
                    atype.value_type, reader, source, location)

            value[item_key] = item_value

        return value

    def _decode_Enum(self, aname, atype, reader, source, location):
        """ Decode to an Enum. """

        self._check_model_type(aname, atype, Enum, location)

        return reader.readElementText()

    def _decode_float(self, aname, atype, reader, source, location):
        """ Decode to a float. """

        self._check_model_type(aname, atype, Float, location)

        value = reader.readElementText()

        try:
            value = float(value)
        except ValueError:
            raise FormatError(
                    "{0}: unable to convert value from '{1}' to a float".format(
                            aname, value),
                    location)

        return value

    def _decode_Instance(self, aname, atype, reader, source, location):
        """ Decode to an instance. """

        # See if we are an item in a collection.
        if isinstance(atype, type):
            if issubclass(atype, Model):
                # Create an instance of the sub-model.
                value = atype()
                self.decode_model(value, reader, source, location)
            else:
                value = self._unpickle_value(aname, reader, location)
        else:
            self._check_model_type(aname, atype, Instance, location)

            if len(atype.types) == 1 and issubclass(atype.types[0], Model):
                # Create an instance of the sub-model.
                value = atype.types[0]()
                self.decode_model(value, reader, source, location)
            else:
                value = self._unpickle_value(aname, reader, location)

        return value

    def _decode_int(self, aname, atype, reader, source, location):
        """ Decode to an int. """

        self._check_model_type(aname, atype, Int, location)

        value = reader.readElementText()

        try:
            value = int(value)
        except ValueError:
            raise FormatError(
                    "{0}: unable to convert value from '{0}' to an int".format(
                            aname, value),
                    location)

        return value

    def _decode_List(self, aname, atype, reader, source, location):
        """ Decode to a list. """

        self._check_model_type(aname, atype, List, location)

        value = []

        while self._next_element(reader, source, location):
            value.append(
                    self._decode_element(reader.name(), aname,
                            atype.element_type, reader, source, location))

        return value

    def _decode_None(self, aname, atype, reader, source, location):
        """ Decode from None. """

        return None

    def _decode_pickle(self, aname, atype, reader, source, location):
        """ Decode from a pickle. """

        return self._unpickle_value(aname, reader, location)

    def _decode_Set(self, aname, atype, reader, source, location):
        """ Decode to a set. """

        self._check_model_type(aname, atype, Set, location)

        value = set()

        while self._next_element(reader, source, location):
            value.add(
                    self._decode_element(reader.name(), aname,
                            atype.element_type, reader, source, location))

        return value

    def _decode_Tuple(self, aname, atype, reader, source, location):
        """ Decode to a tuple. """

        self._check_model_type(aname, atype, Tuple, location)

        value = []

        while self._next_element(reader, source, location):
            value.append(
                    self._decode_element(reader.name(), aname,
                            atype.element_type, reader, source, location))

        return tuple(value)

    def _decode_str(self, aname, atype, reader, source, location):
        """ Decode to a str. """

        self._check_model_type(aname, atype, Str, location)

        return reader.readElementText()

    def _unpickle_value(self, aname, reader, location):
        """ Unpickle a value. """

        value = reader.readElementText()
        value = bytes(value, encoding='utf8')

        try:
            value = base64.b64decode(value)
        except TypeError as e:
            raise FormatError(
                    "{0}: unable to base64 decode value: {1}".format(aname, e),
                    location)

        try:
            value = pickle.loads(value)
        except pickle.UnpicklingError as e:
            raise FormatError(
                    "{0}: unable to unpickle value: {1}".format(aname, e),
                    location)

        return value

    @staticmethod
    def _next_element(reader, source, location):
        """ Get the next start element. """

        while True:
            if reader.readNextStartElement():
                break

            error = reader.error()

            if error == QXmlStreamReader.NoError:
                # All the data has been processed.
                return False

            if error != QXmlStreamReader.PrematureEndOfDocumentError:
                raise FormatError(
                        "XML reader error:{0}: {1}".format(reader.lineNumber(),
                                reader.errorString()),
                        location)

            # Get the next set of data.
            reader.addData(next(source))

        return True

    @staticmethod
    def _check_model_type(aname, atype, element_type, location):
        """ Check that an element type is as expected. """

        if atype is None or isinstance(atype, (Any, element_type)):
            return

        raise FormatError("{0}: has type {1} but is expected to have type "
                "{2}".format(aname, element_type.__name__,
                        type(atype).__name__),
                location)
