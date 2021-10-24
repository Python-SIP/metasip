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


from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QCheckBox, QDialog, QGridLayout

from .Designer.ModulePropertiesBase import Ui_ModulePropertiesBase


class ModulePropertiesDialog(QDialog, Ui_ModulePropertiesBase):
    """ This class implements the dialog for a module's properties. """

    def __init__(self, prj, mod, parent):
        """
        Initialise the dialog.

        prj is the project instance.
        mod is the module instance.
        parent is the parent widget.
        """
        super(ModulePropertiesDialog, self).__init__(parent)

        self.setupUi(self)

        self._ilistall = list(prj.externalmodules)
        self._ilistall.extend([m.name for m in prj.modules])
        self._ilistall.sort()

        # Initialise the dialog.
        self.outputDirSuffix.setText(mod.outputdirsuffix)

        if mod.directives:
            self.additionalDirectives.setPlainText(mod.directives + "\n")

        self.callSuperInitCb.addItems(["Undefined", "No", "Yes"])

        if mod.callsuperinit == 'undefined':
            idx = 0
        elif mod.callsuperinit == 'no':
            idx = 1
        else:
            idx = 2

        self.callSuperInitCb.setCurrentIndex(idx)

        self.virtualErrorHandler.setText(mod.virtualerrorhandler)

        if mod.uselimitedapi:
            self.limitedAPIcb.setCheckState(Qt.Checked)

        if mod.pyssizetclean:
            self.ssizetCleanCb.setCheckState(Qt.Checked)

        layout = QGridLayout()

        for i, itm in enumerate(self._ilistall):
            cb = QCheckBox(itm)

            if mod.name == itm:
                cb.setEnabled(False)
            elif itm in mod.imports:
                cb.setCheckState(Qt.Checked)

            layout.addWidget(cb, i // 2, i % 2)

        self.imports.setLayout(layout)

    def fields(self):
        """ Return a tuple of the dialog fields. """

        odirsuff = self.outputDirSuffix.text().strip()
        adddirectives = self.additionalDirectives.toPlainText().strip()
        callsuperinit = self.callSuperInitCb.currentText().lower()
        virtualerrorhandler = self.virtualErrorHandler.text().strip()
        uselimitedapi = (self.limitedAPIcb.checkState() == Qt.Checked)
        pyssizetclean = (self.ssizetCleanCb.checkState() == Qt.Checked)

        il = []

        i = 0

        layout = self.imports.layout()

        for i in range(layout.count()):
            cb = layout.itemAt(i).widget()
            if cb.checkState() == Qt.Checked:
                il.append(self._ilistall[i])

        return (odirsuff, il, adddirectives, callsuperinit,
                virtualerrorhandler, uselimitedapi, pyssizetclean)
