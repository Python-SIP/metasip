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


""" This module handles an opaque class's properties. """


from PyQt4.QtGui import QDialog

from .Designer.OpaqueClassPropertiesBase import Ui_OpaqueClassPropertiesBase


class OpaqueClassPropertiesDialog(QDialog, Ui_OpaqueClassPropertiesBase):
    """
    This class implements the dialog for a class's properties.
    """
    def __init__(self, cls, parent):
        """
        Initialise the dialog.

        cls is the opaque class instance.
        parent is the parent widget.
        """
        super(OpaqueClassPropertiesDialog, self).__init__(parent)

        self.setupUi(self)

        # Initialise the dialog.
        for a in cls.annos.split(','):
            al = a.split("=")
            name = al[0]

            cb = None

            if name == "External":
                cb = self.externalCb

            if cb:
                cb.setChecked(True)

    def fields(self):
        """
        Return a tuple of the dialog fields.
        """
        alist = []

        if self.externalCb.isChecked():
            alist.append("External")

        return (",".join(alist), )
