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


""" This module handles a header directory's properties. """


from PyQt4.QtGui import QDialog

from .Designer.HeaderDirectoryPropertiesBase import Ui_HeaderDirectoryPropertiesBase


class HeaderDirectoryPropertiesDialog(QDialog, Ui_HeaderDirectoryPropertiesBase):
    """
    This class implements the dialog for a header directory's properties.
    """
    def __init__(self, hdir, parent):
        """
        Initialise the dialog.

        hdir is the header directory instance.
        parent is the parent widget.
        """
        super(HeaderDirectoryPropertiesDialog, self).__init__(parent)

        self.setupUi(self)

        # Initialise the dialog.
        self.inputDirSuffix.setText(hdir.inputdirsuffix)
        self.fileFilter.setText(hdir.filefilter)
        self.parserCmdLine.setText(hdir.parserargs)

    def fields(self):
        """
        Return a tuple of the dialog fields.
        """
        suff = str(self.inputDirSuffix.text()).strip()
        filter = str(self.fileFilter.text()).strip()
        pargs = str(self.parserCmdLine.text()).strip()

        return (suff, filter, pargs)
