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


""" This module handles a namespace's properties. """


from PyQt5.QtWidgets import QDialog

from .Designer.NamespacePropertiesBase import Ui_NamespacePropertiesBase
from .Annos import split_annos


class NamespacePropertiesDialog(QDialog, Ui_NamespacePropertiesBase):
    """
    This class implements the dialog for a namespace's properties.
    """
    def __init__(self, cls, parent):
        """
        Initialise the dialog.

        cls is the opaque class instance.
        parent is the parent widget.
        """
        super().__init__(parent)

        self.setupUi(self)

        # Initialise the dialog.
        for name, value in split_annos(cls.annos):
            cb = None

            if name == "PyQtNoQMetaObject":
                cb = self.externalCb

            if cb:
                cb.setChecked(True)

    def fields(self):
        """
        Return a tuple of the dialog fields.
        """
        alist = []

        if self.externalCb.isChecked():
            alist.append("PyQtNoQMetaObject")

        return (",".join(alist), )
