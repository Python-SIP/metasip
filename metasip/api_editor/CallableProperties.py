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

from ..Project import (Constructor, Destructor, Method, OperatorMethod,
        Function, OperatorFunction, ManualCode)

from .Designer.CallablePropertiesBase import Ui_CallablePropertiesBase
from .Encoding import Encoding


class CallablePropertiesDialog(QDialog, Ui_CallablePropertiesBase):
    """
    This class implements the dialog for callable properties.
    """
    def __init__(self, code, parent):
        """
        Initialise the dialog.

        code is the code instance.
        parent is the parent widget.
        """
        super(CallablePropertiesDialog, self).__init__(parent)

        self.setupUi(self)

        # Initialise the dialog.
        self._encoding = Encoding(self.encodingCb)

        if isinstance(code, Constructor):
            cap = "Constructor Properties"
            self.pyType.setEnabled(False)
            self.pyArgs.setText(code.pyargs)

            self.autoGen.setEnabled(False)
            self.docType.setEnabled(False)
            self.encodingCb.setEnabled(False)
            self.factoryCb.setEnabled(False)
            self.keepRefCb.setEnabled(False)
            self.lenCb.setEnabled(False)
            self.newThreadCb.setEnabled(False)
            self.noArgParserCb.setEnabled(False)
            self.noCopyCb.setEnabled(False)
            self.numericCb.setEnabled(False)
            self.transferBackCb.setEnabled(False)
            self.transferThisCb.setEnabled(False)
            self.pyName.setEnabled(False)
        elif isinstance(code, Destructor):
            cap = "Destructor Properties"
            self.pyType.setEnabled(False)
            self.pyArgs.setEnabled(False)

            self.api.setEnabled(False)
            self.autoGen.setEnabled(False)
            self.defaultCb.setEnabled(False)
            self.docType.setEnabled(False)
            self.encodingCb.setEnabled(False)
            self.factoryCb.setEnabled(False)
            self.keepRefCb.setEnabled(False)
            self.lenCb.setEnabled(False)
            self.newThreadCb.setEnabled(False)
            self.noArgParserCb.setEnabled(False)
            self.noCopyCb.setEnabled(False)
            self.noDerivedCb.setEnabled(False)
            self.numericCb.setEnabled(False)
            self.postHook.setEnabled(False)
            self.preHook.setEnabled(False)
            self.transferCb.setEnabled(False)
            self.transferBackCb.setEnabled(False)
            self.transferThisCb.setEnabled(False)
            self.pyName.setEnabled(False)
        elif isinstance(code, Method):
            cap = "Method Properties"
            self.pyType.setText(code.pytype)
            self.pyArgs.setText(code.pyargs)

            self.defaultCb.setEnabled(False)
            self.noDerivedCb.setEnabled(False)
        elif isinstance(code, OperatorMethod):
            cap = "Operator Method Properties"
            self.pyType.setText(code.pytype)
            self.pyArgs.setText(code.pyargs)

            self.defaultCb.setEnabled(False)
            self.keepRefCb.setEnabled(False)
            self.lenCb.setEnabled(False)
            self.noArgParserCb.setEnabled(False)
            self.noDerivedCb.setEnabled(False)
            self.pyName.setEnabled(False)
        elif isinstance(code, Function):
            cap = "Function Properties"
            self.pyType.setText(code.pytype)
            self.pyArgs.setText(code.pyargs)

            self.defaultCb.setEnabled(False)
            self.keepRefCb.setEnabled(False)
            self.lenCb.setEnabled(False)
            self.noCopyCb.setEnabled(False)
            self.noDerivedCb.setEnabled(False)
            self.transferCb.setEnabled(False)
            self.transferThisCb.setEnabled(False)
        elif isinstance(code, OperatorFunction):
            cap = "Operator Function Properties"
            self.pyType.setText(code.pytype)
            self.pyArgs.setText(code.pyargs)

            self.defaultCb.setEnabled(False)
            self.keepRefCb.setEnabled(False)
            self.lenCb.setEnabled(False)
            self.noArgParserCb.setEnabled(False)
            self.noCopyCb.setEnabled(False)
            self.noDerivedCb.setEnabled(False)
            self.transferCb.setEnabled(False)
            self.transferThisCb.setEnabled(False)
            self.pyName.setEnabled(False)
        elif isinstance(code, ManualCode):
            cap = "Manual Code Properties"
            self.pyType.setEnabled(False)
            self.pyArgs.setEnabled(False)
            self.pyName.setEnabled(False)

        self.setWindowTitle(cap)

        for a in code.annos.split(','):
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

            if name == "API":
                le = self.api
            elif name == "AutoGen":
                le = self.autoGen

                if not value:
                    value = "All"
            elif name == "Default":
                cb = self.defaultCb
            elif name == "DocType":
                le = self.docType
            elif name == "Encoding":
                self._encoding.setAnnotation(a)
            elif name == "Factory":
                cb = self.factoryCb
            elif name == "HoldGIL":
                cb = self.holdGILCb
            elif name == "KeepReference":
                cb = self.keepRefCb
            elif name == "__len__":
                cb = self.lenCb
            elif name == "NewThread":
                cb = self.newThreadCb
            elif name == "NoArgParser":
                cb = self.noArgParserCb
            elif name == "NoCopy":
                cb = self.noCopyCb
            elif name == "NoDerived":
                cb = self.noDerivedCb
            elif name == "Numeric":
                cb = self.numericCb
            elif name == "PostHook":
                le = self.postHook
            elif name == "PreHook":
                le = self.preHook
            elif name == "PyName":
                le = self.pyName
            elif name == "ReleaseGIL":
                cb = self.releaseGILCb
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

    def fields(self):
        """
        Return a tuple of the dialog fields.
        """
        pytype = str(self.pyType.text()).strip()
        pyargs = str(self.pyArgs.text()).strip()

        alist = []

        s = str(self.api.text()).strip()
        if s:
            alist.append("API=" + s)

        s = str(self.autoGen.text()).strip()
        if s:
            if s == "All":
                alist.append("AutoGen")
            else:
                alist.append("AutoGen=" + s)

        if self.defaultCb.isChecked():
            alist.append("Default")

        s = str(self.docType.text()).strip()
        if s:
            alist.append("DocType=\"%s\"" % s)

        self._encoding.annotation(alist)

        if self.factoryCb.isChecked():
            alist.append("Factory")

        if self.holdGILCb.isChecked():
            alist.append("HoldGIL")

        if self.keepRefCb.isChecked():
            alist.append("KeepReference")

        if self.lenCb.isChecked():
            alist.append("__len__")

        if self.newThreadCb.isChecked():
            alist.append("NewThread")

        if self.noArgParserCb.isChecked():
            alist.append("NoArgParser")

        if self.noCopyCb.isChecked():
            alist.append("NoCopy")

        if self.noDerivedCb.isChecked():
            alist.append("NoDerived")

        if self.numericCb.isChecked():
            alist.append("Numeric")

        s = str(self.postHook.text()).strip()
        if s:
            alist.append("PostHook=" + s)

        s = str(self.preHook.text()).strip()
        if s:
            alist.append("PreHook=" + s)

        s = str(self.pyName.text()).strip()
        if s:
            alist.append("PyName=" + s)

        if self.releaseGILCb.isChecked():
            alist.append("ReleaseGIL")

        if self.transferCb.isChecked():
            alist.append("Transfer")

        if self.transferBackCb.isChecked():
            alist.append("TransferBack")

        if self.transferThisCb.isChecked():
            alist.append("TransferThis")

        return (pytype, pyargs, ",".join(alist))