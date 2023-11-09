# Copyright (c) 2023 Riverbank Computing Limited.
#
# This file is part of metasip.
#
# This file may be used under the terms of the GNU General Public License v3
# as published by the Free Software Foundation which can be found in the file
# LICENSE-GPL3.txt included in this package.
#
# This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
# WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.


from PyQt6.QtCore import QFile, QIODevice, QUrl
from PyQt6.QtXmlPatterns import (QAbstractMessageHandler, QSourceLocation,
        QXmlSchema, QXmlSchemaValidator)

from ...dip.model import Instance, Model, Str


class _MessageHandler(QAbstractMessageHandler, Model):
    """ This is an internal class that implements a message handler for
    QXmlSchema.
    """

    # The location of the error that triggered the message.
    location = Instance(QSourceLocation)

    # The message.
    message = Str()

    def handleMessage(self, type, message, identifier, location):
        """ Reimplemented to handle the message. """

        self.message = message
        self.location = location


class SchemaValidator(Model):
    """ The SchemaValidator class implements an XML schema validator using
    PyQt6's QXmlSchemaValidator.
    """

    # The message handler.
    message_handler = Instance(_MessageHandler)

    def validate(self, xsd, xml):
        """ Validate an XML file against a schema.  An IOError is raised if
        either the XML file or the schema file could not be opened.  A
        SchemaValidationError is raised if the XML could not be validated.

        :param xsd:
            is the name of the schema file.
        :param xml:
            is the name of the XML file.
        """

        xsd_file = QFile(xsd)
        if not xsd_file.open(QIODevice.OpenModeFlag.ReadOnly):
            raise IOError("unable to open schema file {0}".format(xsd))

        xsd = QXmlSchema()
        xsd.setMessageHandler(self.message_handler)
        xsd.load(xsd_file, QUrl.fromLocalFile(xsd_file.fileName()))

        if not xsd.isValid():
            raise SchemaValidationException(self.message_handler)

        xml_file = QFile(xml)
        if not xml_file.open(QIODevice.OpenModeFlag.ReadOnly):
            raise IOError("unable to open XML file {0}".format(xml))

        validator = QXmlSchemaValidator(xsd)
        if not validator.validate(xml_file, QUrl.fromLocalFile(xml_file.fileName())):
            raise SchemaValidationException(self.message_handler)

    @message_handler.default
    def message_handler(self):
        """ Invoked to return the default message handler. """

        return _MessageHandler()


class SchemaValidationException(Exception):
    """ The SchemaValidationException describes a schema validation error. """

    def __init__(self, message_handler):
        """ Initialise the exception.

        :param message_handler:
            is the message handler.
        """

        location = message_handler.location

        self.filename = location.uri().toLocalFile()
        self.line = location.line()
        self.column = location.column()

        super().__init__(message_handler.message)
