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


""" This module handles an enum's properties. """


from PyQt4.QtGui import QDialog

from .Designer.EnumPropertiesBase import Ui_EnumPropertiesBase


class EnumPropertiesDialog(QDialog, Ui_EnumPropertiesBase):
    """
    This class implements the dialog for an enum's properties.
    """
    def __init__(self, cls, parent):
        """
        Initialise the dialog.

        cls is the class instance.
        parent is the parent widget.
        """
        super(EnumPropertiesDialog, self).__init__(parent)

        self.setupUi(self)

        # Initialise the dialog.
        for a in cls.annos.split(','):
            al = a.split("=")
            name = al[0]

            le = None

            if name == "PyName":
                le = self.pyName

            if le:
                le.setText(al[1])

    def fields(self):
        """
        Return a tuple of the dialog fields.
        """
        alist = []

        s = str(self.pyName.text()).strip()
        if s:
            alist.append("PyName=" + s)

        return (",".join(alist), )
