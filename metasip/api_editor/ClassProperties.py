# Copyright (c) 2013 Riverbank Computing Limited.
#
# This file is part of metasip.
#
# This file may be used under the terms of the GNU General Public License v3
# as published by the Free Software Foundation which can be found in the file
# LICENSE-GPL3.txt included in this package.
#
# This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
# WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.


""" This module handles a class's properties. """


from PyQt4.QtGui import QDialog

from .Designer.ClassPropertiesBase import Ui_ClassPropertiesBase


class ClassPropertiesDialog(QDialog, Ui_ClassPropertiesBase):
    """
    This class implements the dialog for a class's properties.
    """
    def __init__(self, cls, parent):
        """
        Initialise the dialog.

        cls is the class instance.
        parent is the parent widget.
        """
        super(ClassPropertiesDialog, self).__init__(parent)

        self.setupUi(self)

        # Initialise the dialog.
        self.pyBaseClasses.setText(cls.pybases)

        for a in cls.annos.split(','):
            al = a.split("=")
            name = al[0]

            cb = None
            le = None

            if name == "Abstract":
                cb = self.abstractCb
            elif name == "AllowNone":
                cb = self.allownoneCb
            elif name == "DelayDtor":
                cb = self.delaydtorCb
            elif name == "NoDefaultCtors":
                cb = self.nodefaultctorsCb
            elif name == "PyQt4NoQMetaObject":
                cb = self.noqmetaobjectCb
            elif name == "ExportGeneratedDerived":
                cb = self.exportgenderivedCb
            elif name == "Mixin":
                cb = self.mixinCb
            elif name == "PyName":
                le = self.pyName
            elif name == "API":
                le = self.api
            elif name == "Metatype":
                le = self.metatype
            elif name == "Supertype":
                le = self.supertype
            elif name == "PyQtInterface":
                le = self.interface

            if cb:
                cb.setChecked(True)
            elif le:
                le.setText(al[1])

    def fields(self):
        """
        Return a tuple of the dialog fields.
        """
        pybases = " ".join(self.pyBaseClasses.text().strip().split())

        alist = []

        if self.abstractCb.isChecked():
            alist.append("Abstract")

        if self.allownoneCb.isChecked():
            alist.append("AllowNone")

        if self.delaydtorCb.isChecked():
            alist.append("DelayDtor")

        if self.nodefaultctorsCb.isChecked():
            alist.append("NoDefaultCtors")

        if self.noqmetaobjectCb.isChecked():
            alist.append("PyQt4NoQMetaObject")

        if self.exportgenderivedCb.isChecked():
            alist.append("ExportGeneratedDerived")

        if self.mixinCb.isChecked():
            alist.append("Mixin")

        s = self.pyName.text().strip()
        if s:
            alist.append("PyName=" + s)

        s = self.api.text().strip()
        if s:
            alist.append("API=" + s)

        s = self.metatype.text().strip()
        if s:
            alist.append("Metatype=" + s)

        s = self.supertype.text().strip()
        if s:
            alist.append("Supertype=" + s)

        s = self.interface.text().strip()
        if s:
            alist.append("PyQtInterface=" + s)

        return (pybases, ",".join(alist))
