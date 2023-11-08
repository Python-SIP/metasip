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


from PyQt6.QtWidgets import QDialog

from .Designer.EnumPropertiesBase import Ui_EnumPropertiesBase
from .Annos import split_annos
from .BaseType import BaseType


class EnumPropertiesDialog(QDialog, Ui_EnumPropertiesBase):
    """ This class implements the dialog for an enum's properties. """

    def __init__(self, enum, parent):
        """ Initialise the dialog. """

        super().__init__(parent)

        self.setupUi(self)

        # Initialise the dialog.
        self._base_type = BaseType(self.baseTypeCb)

        for name, value in split_annos(enum.annos):
            le = None
            cb = None

            if name == "BaseType":
                self._base_type.setAnnotation(value)
            elif name == "PyName":
                le = self.pyName
            elif name == "NoScope":
                cb = self.noScopeCb
            elif name == "NoTypeHint":
                cb = self.noTypeHintCb

            if cb is not None:
                cb.setChecked(True)
            elif le is not None:
                le.setText(value)

    def fields(self):
        """
        Return a tuple of the dialog fields.
        """
        alist = []

        self._base_type.annotation(alist)

        s = self.pyName.text().strip()
        if s != '':
            alist.append("PyName=" + s)

        if self.noScopeCb.isChecked():
            alist.append("NoScope")

        if self.noTypeHintCb.isChecked():
            alist.append("NoTypeHint")

        return (','.join(alist), )
