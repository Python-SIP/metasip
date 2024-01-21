# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


from xml.sax import make_parser, SAXParseException
from xml.sax.handler import ContentHandler, ErrorHandler


class ParserBase(ContentHandler):
    """
    The base class for all MetaSIP XML parsers.  Sub-classes implement methods
    with the same name as the elements they deal with (with "Start" or "End"
    appended).
    """
    def __init__(self):
        """
        Initialise the parser instance.
        """
        ContentHandler.__init__(self)

        self.diagnostic = None

        self._parser = make_parser()
        self._parser.setContentHandler(self)

    def classMap(self):
        """
        The default implementation to return an empty class map.
        """
        return {}

    def _findClass(self, name):
        """
        Return the class corresponding to the given name, or None if none.

        name is the name.
        """
        return self.classMap().get(name)

    def _findMethod(self, name):
        """
        Return the bound method with the given name.
        """
        try:
            m = getattr(self, name)
        except AttributeError:
            m = None

        return m

    def startElement(self, name, attrs):
        """
        The start-of-an-element callback.

        name is the element name.
        attrs is the dictionary of attributes.
        """
        name = name.lower()

        m = self._findClass(name)

        if m:
            m(self, attrs)
        else:
            m = self._findMethod(name + "Start")

            if m:
                m(attrs)

    def endElement(self, name):
        """
        The end-of-an-element callback.

        name is the element name.
        """
        name = name.lower()

        if self._findClass(name):
            return

        m = self._findMethod(name + "End")

        if m:
            m()

    def parse(self, ifname):
        """ Parse an XML file.

        :param ifname:
            is the name of a file or a file object to parse.
        :return:
            ``True`` if the file was parsed successfully.
        """

        eh = _ParserErrorHandler()

        self._parser.setErrorHandler(eh)

        try:
            self._parser.parse(ifname)
        except SAXParseException:
            self.diagnostic = eh.diagnostic
            return False

        return True


class _ParserErrorHandler(ErrorHandler):
    """ This is the SAX error handler. """

    def __init__(self):
        """ Initialise the error handler. """

        self.diagnostic = None

    def error(self, exception):
        """ Handle recoverable errors (where parsing might continue). """

        xs = str(exception)

        self.shell.log(xs)

        if not self.diagnostic:
            self.diagnostic = xs

        raise exception

    def fatalError(self, exception):
        """ Handle non-recoverable errors (where parsing can't continue). """

        xs = str(exception)

        self.shell.log(xs)

        if not self.diagnostic:
            self.diagnostic = xs

        raise exception

    def warning(self, exception):
        """ Handle warnings. """

        self.shell.log(str(exception))


def optAttribute(attrs, name, default=''):
    """ Return the value of an optional attribute.

    :param attrs:
        is the dictionary of attributes.
    :param name:
        is the name of the attribute to return.
    :param default:
        is the value to return if the attribute wasn't specified.
    :return:
        the value of the attribute.
    """

    try:
        return attrs[name]
    except KeyError:
        return default
