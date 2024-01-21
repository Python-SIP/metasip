# SPDX-License-Identifier: BSD-2-Clause

# Copyright (c) 2024 Phil Thompson <phil@riverbankcomputing.com>


from ..exceptions import UserException


class IndentFile:
    """ This is a thin wrapper around a file object that supports indentation.
    """

    def __init__(self, file_name, indent):
        """ Create a file for writing. """

        self._f = open(file_name, 'w', encoding='UTF-8')
        self._indent = indent
        self._nr_indents = 0
        self._indent_next = True
        self._blank = False
        self._suppress_blank = False

        self.name = file_name

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
    def create(cls, file_name, indent=4):
        """ Return an indent file or raise an exception if there was an error.
        """

        try:
            return cls(file_name, indent)
        except IOError as e:
            raise UserException(f"There was an error creating '{file_name}'",
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
