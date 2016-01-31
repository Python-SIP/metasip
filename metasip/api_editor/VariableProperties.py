# Copyright (c) 2016 Riverbank Computing Limited.
#
# This file is part of metasip.
#
# This file may be used under the terms of the GNU General Public License v3
# as published by the Free Software Foundation which can be found in the file
# LICENSE-GPL3.txt included in this package.
#
# This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
# WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.


""" This module handles a variable's properties. """


from PyQt4.QtGui import QDialog

from .Designer.VariablePropertiesBase import Ui_VariablePropertiesBase
from .Encoding import Encoding


class VariablePropertiesDialog(QDialog, Ui_VariablePropertiesBase):
    """
    This class implements the dialog for a variables's properties.
    """
    def __init__(self, cls, parent):
        """
        Initialise the dialog.

        cls is the class instance.
        parent is the parent widget.
        """
        super(VariablePropertiesDialog, self).__init__(parent)

        self.setupUi(self)

        # Initialise the dialog.
        self._encoding = Encoding(self.encodingCb)

        for a in cls.annos.split(','):
            al = a.split("=")
            name = al[0]

            if len(al) == 2:
                value = al[1]

                if value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
            else:
                value = None

            cb = None
            le = None

            if name == "DocType":
                le = self.docType
            elif name == "Encoding":
                self._encoding.setAnnotation(a)
            elif name == "NoSetter":
                cb = self.noSetterCb
            elif name == "PyInt":
                cb = self.pyIntCb
            elif name == "PyName":
                le = self.pyName
            elif name == "TypeHint":
                le = self.typeHint

            if cb:
                cb.setChecked(True)
            elif le:
                le.setText(value)

    def fields(self):
        """
        Return a tuple of the dialog fields.
        """
        alist = []

        self._encoding.annotation(alist)

        s = str(self.docType.text()).strip()
        if s:
            alist.append("DocType=\"%s\"" % s)

        if self.noSetterCb.isChecked():
            alist.append("NoSetter")

        if self.pyIntCb.isChecked():
            alist.append("PyInt")

        s = str(self.pyName.text()).strip()
        if s:
            alist.append("PyName=" + s)

        s = str(self.typeHint.text()).strip()
        if s:
            alist.append("TypeHint=\"%s\"" % s)

        return (",".join(alist), )
