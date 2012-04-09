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


""" This module handles a code item's generations. """


import sys

from PyQt4.QtGui import QDialog

from .Designer.GenerationsBase import Ui_GenerationsBase


class GenerationsDialog(QDialog, Ui_GenerationsBase):
    """
    This class implements the dialog for generations.
    """
    def __init__(self, prj, sgen, egen, parent):
        """
        Initialise the dialog.

        prj is the containing project.
        sgen is the current start generation.
        egen is the current end generation.
        parent is the parent widget.
        """
        super(GenerationsDialog, self).__init__(parent)

        self.setupUi(self)

        # Initialise the dialog.
        self.sgen.addItem("First")

        for v in prj.versions:
            self.sgen.addItem(v)
            self.egen.addItem(v)

        self.egen.addItem("Latest")

        self.sgen.setCurrentIndex(sgen)

        if egen >= self.egen.count():
            last = self.egen.count()
        else:
            last = egen

        self.egen.setCurrentIndex(last - 1)

    def fields(self):
        """
        Return a tuple of the dialog fields.
        """
        sgen = self.sgen.currentIndex()
        egen = self.egen.currentIndex() + 1

        if egen == self.egen.count():
            egen = sys.maxsize

        return (sgen, egen)
