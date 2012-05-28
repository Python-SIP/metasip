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


""" This module handles argument properties. """


from PyQt4.QtGui import QDialog

from .Designer.ArgPropertiesBase import Ui_ArgPropertiesBase
from .Encoding import Encoding


class ArgPropertiesDialog(QDialog, Ui_ArgPropertiesBase):
    """
    This class implements the dialog for argument properties.
    """
    def __init__(self, arg, parent):
        """
        Initialise the dialog.

        arg is the argument instance.
        parent is the parent widget.
        """
        super(ArgPropertiesDialog, self).__init__(parent)

        self.setupUi(self)

        # Initialise the dialog.
        self._encoding = Encoding(self.encodingCb)

        if arg.name is not None:
            self.name.setText(arg.name)

        self.unnamedCb.setChecked(arg.unnamed)
        self.pyType.setText(arg.pytype)

        self.keepRefCb.stateChanged.connect(self._update_ref)

        for a in arg.annos.split(','):
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

            if name == "AllowNone":
                cb = self.allowNoneCb
            elif name == "Array":
                cb = self.arrayCb
            elif name == "ArraySize":
                cb = self.arraySizeCb
            elif name == "Constrained":
                cb = self.constrainedCb
            elif name == "DocType":
                le = self.docType
            elif name == "DocValue":
                le = self.docValue
            elif name == "Encoding":
                self._encoding.setAnnotation(a)
            elif name == "GetWrapper":
                cb = self.getWrapperCb
            elif name == "In":
                cb = self.inCb
            elif name == "KeepReference":
                cb = self.keepRefCb

                if value is not None:
                    self.ref.setText(value)
            elif name == "NoCopy":
                cb = self.noCopyCb
            elif name == "Out":
                cb = self.outCb
            elif name == "PyInt":
                cb = self.pyIntCb
            elif name == "ResultSize":
                cb = self.resultSizeCb
            elif name == "SingleShot":
                cb = self.singleShotCb
            elif name == "Transfer":
                cb = self.transferCb
            elif name == "TransferBack":
                cb = self.transferBackCb
            elif name == "TransferThis":
                cb = self.transferThisCb

            if cb:
                cb.setChecked(True)
            elif le:
                le.setText(value)

        self._update_ref()

    def fields(self):
        """
        Return a tuple of the dialog fields.
        """
        name = str(self.name.text()).strip()
        if name == "":
            name = None

        unnamed = self.unnamedCb.isChecked()
        pytype = str(self.pyType.text()).strip()

        alist = []

        if self.allowNoneCb.isChecked():
            alist.append("AllowNone")

        if self.arrayCb.isChecked():
            alist.append("Array")

        if self.arraySizeCb.isChecked():
            alist.append("ArraySize")

        if self.constrainedCb.isChecked():
            alist.append("Constrained")

        s = str(self.docType.text()).strip()
        if s:
            alist.append("DocType=\"%s\"" % s)

        s = str(self.docValue.text()).strip()
        if s:
            alist.append("DocValue=\"%s\"" % s)

        self._encoding.annotation(alist)

        if self.getWrapperCb.isChecked():
            alist.append("GetWrapper")

        if self.inCb.isChecked():
            alist.append("In")

        if self.keepRefCb.isChecked():
            s = str(self.ref.text()).strip()
            if s:
                alist.append("KeepReference=" + s)
            else:
                alist.append("KeepReference")

        if self.noCopyCb.isChecked():
            alist.append("NoCopy")

        if self.outCb.isChecked():
            alist.append("Out")

        if self.pyIntCb.isChecked():
            alist.append("PyInt")

        if self.resultSizeCb.isChecked():
            alist.append("ResultSize")

        if self.singleShotCb.isChecked():
            alist.append("SingleShot")

        if self.transferCb.isChecked():
            alist.append("Transfer")

        if self.transferBackCb.isChecked():
            alist.append("TransferBack")

        if self.transferThisCb.isChecked():
            alist.append("TransferThis")

        return (name, unnamed, pytype, ",".join(alist))

    def _update_ref(self, state=None):
        """
        Enable the reference field if the keep reference field is checked.
        """
        checked = self.keepRefCb.isChecked()
        self.refLab.setEnabled(checked)
        self.ref.setEnabled(checked)