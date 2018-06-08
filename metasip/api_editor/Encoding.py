# Copyright (c) 2018 Riverbank Computing Limited.
#
# This file is part of metasip.
#
# This file may be used under the terms of the GNU General Public License v3
# as published by the Free Software Foundation which can be found in the file
# LICENSE-GPL3.txt included in this package.
#
# This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
# WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.


""" This module handles the Encoding annotation. """


class Encoding(object):
    """
    This class implements helpers for the Encoding annotation.
    """

    ENCODINGS = ("Default", "None", "ASCII", "Latin-1", "UTF-8")

    def __init__(self, combo):
        """
        Initialise the combo-box.

        combo is the combo-box.
        """
        combo.addItems(self.ENCODINGS)

        self._combo = combo

    def setAnnotation(self, anno):
        """
        Set the current annotation.
        """
        for index, encoding in enumerate(self.ENCODINGS):
            if encoding == anno:
                self._combo.setCurrentIndex(index)
                break;

    def annotation(self, alist):
        """
        Get the current annotation.
        """
        encoding = str(self._combo.currentText())

        if encoding != "Default":
            alist.append('Encoding="%s"' % encoding)
