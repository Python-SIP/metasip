# Copyright (c) 2021 Riverbank Computing Limited.
#
# This file is part of metasip.
#
# This file may be used under the terms of the GNU General Public License v3
# as published by the Free Software Foundation which can be found in the file
# LICENSE-GPL3.txt included in this package.
#
# This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
# WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.


class BaseType:
    """ This class implements helpers for the BaseType annotation. """

    BASE_TYPES = ("Enum", "Flag", "IntEnum", "UIntEnum", "IntFlag")

    def __init__(self, combo):
        """ Initialise the combo-box. """

        combo.addItems(self.BASE_TYPES)

        self._combo = combo

    def setAnnotation(self, anno):
        """ Set the current annotation. """

        for index, base_type in enumerate(self.BASE_TYPES):
            if base_type == anno:
                self._combo.setCurrentIndex(index)
                break;

    def annotation(self, alist):
        """ Get the current annotation. """

        base_type = str(self._combo.currentText())

        if base_type != "Enum":
            alist.append('BaseType=%s' % base_type)
