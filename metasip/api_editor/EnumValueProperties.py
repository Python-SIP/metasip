# Copyright (c) 2017 Riverbank Computing Limited.
#
# This file is part of metasip.
#
# This file may be used under the terms of the GNU General Public License v3
# as published by the Free Software Foundation which can be found in the file
# LICENSE-GPL3.txt included in this package.
#
# This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
# WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.


""" This module handles an enum value's properties. """


from PyQt5.QtWidgets import QDialog

from .Designer.EnumValuePropertiesBase import Ui_EnumValuePropertiesBase
from .Annos import split_annos


class EnumValuePropertiesDialog(QDialog, Ui_EnumValuePropertiesBase):
    """
    This class implements the dialog for an enum value's properties.
    """
    def __init__(self, cls, parent):
        """
        Initialise the dialog.

        cls is the class instance.
        parent is the parent widget.
        """
        super(EnumValuePropertiesDialog, self).__init__(parent)

        self.setupUi(self)

        # Initialise the dialog.
        for name, value in split_annos(cls.annos):
            cb = None
            le = None

            if name == "NoTypeHint":
                cb = self.noTypeHintCb
            elif name == "PyName":
                le = self.pyName

            if cb:
                cb.setChecked(True)
            elif le:
                le.setText(value)

    def fields(self):
        """
        Return a tuple of the dialog fields.
        """
        alist = []

        if self.noTypeHintCb.isChecked():
            alist.append("NoTypeHint")

        s = str(self.pyName.text()).strip()
        if s:
            alist.append("PyName=" + s)

        return (",".join(alist), )
