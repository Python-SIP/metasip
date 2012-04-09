# Copyright (c) 2012 Riverbank Computing Limited.
#
# This file is part of metasip.
#
# This file may be used under the terms of the GNU General Public License v3
# as published by the Free Software Foundation which can be found in the file
# LICENSE-GPL3.txt included in this package.
#
# This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
# WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.


""" This module implements the support for the WebXML output of qdoc. """


from . import Parser


class WebXMLParser(Parser.ParserBase):
    """
    This is the WebXML file parser.
    """

    def parse(self, webxml, callables, ui):
        """
        Parse a WebXML file.

        webxml is the name of the WebXML file.
        callables is the dictionary of callables to update.
        ui is the user interface instance.
        """

        self._callables = callables
        self._current_prefix = None

        if not Parser.ParserBase.parse(self, webxml, ui):
            raise Exception(self.diagnostic)

        return self._callables

    def functionStart(self, attrs):
        """ Called at the end of a function tag. """

        try:
            fullname = attrs['fullname']
        except KeyError:
            self._current = None
            return

        if self._bool_value(attrs, 'static'):
            static = 'static '
        else:
            static = ''

        if self._bool_value(attrs, 'const'):
            const = ' const'
        else:
            const = ''

        self._current = '%s%s(%%s)%s' % (static, fullname, const)

        self._current_args = []

    def functionEnd(self):
        """ Called at the end of a function tag. """

        if self._current is None:
            return

        arg_types = []
        arg_names = []
        for type, name in self._current_args:
            arg_types.append(type)
            arg_names.append(name)

        sig = self._current % ', '.join(arg_types)
        self._callables[sig] = arg_names

        self._current = None

    def parameterStart(self, attrs):
        """ Called at the start of a parameter tag. """

        if self._current is None:
            return

        left = attrs['left'].replace(' ', '')
        if left.startswith('const'):
            left = 'const ' + left[5:]

        name = attrs.get('name', '')

        self._current_args.append((left, name))

    @staticmethod
    def _bool_value(attrs, aname):
        """ Return the boolean value of the given attribute. """

        try:
            attr = attrs[aname]
        except KeyError:
            return False

        if attr == "true":
            return True

        return False
