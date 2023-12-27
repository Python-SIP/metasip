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


from ..exceptions import UserException


class IndentFile:
    """ This is a thin wrapper around a file object that supports indentation.
    """

    def __init__(self, fname, indent):
        """ Create a file for writing. """

        self._f = open(fname, 'w', encoding='UTF-8')
        self._indent = indent
        self._nr_indents = 0
        self._indent_next = True
        self._blank = False
        self._suppress_blank = False

        self.name = fname

    def __iadd__(self, by):
        """ Increase the indentation. """

        self._nr_indents += by
        self._suppress_blank = True

        return self

    def __isub__(self, by):
        """ Decrease the indentation. """

        self._nr_indents -= by
        self._blank = False
        self._suppress_blank = False

        return self

    def blank(self):
        """ Write a blank line. """

        if not self._suppress_blank:
            self._blank = True

    def close(self):
        """ Close the file. """

        self._f.close()

    @classmethod
    def create(cls, fname, indent=4):
        """ Return an indent file or raise an exception if there was an error.
        """

        try:
            return cls(fname, indent)
        except IOError as e:
            raise UserException(f"There was an error creating '{fname}'",
                    detail=str(e)) from e

    def write(self, data, indent=True):
        """ Write data to the file with optional automatic indentation. """

        if data:
            if self._blank:
                self._f.write('\n')
                self._blank = False

            lines = data.split('\n')

            for l in lines[:-1]:
                if indent and self._indent_next:
                    self._f.write(' ' * (self._indent * self._nr_indents))

                self._f.write(l + '\n')
                self._indent_next = True

            # Handle the last line.
            l = lines[-1]

            if l:
                if indent and self._indent_next:
                    self._f.write(' ' * (self._indent * self._nr_indents))

                self._f.write(l)
                self._indent_next = False
            else:
                self._indent_next = True

            self._suppress_blank = False
