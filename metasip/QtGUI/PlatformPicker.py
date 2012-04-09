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


""" This module handles the selection of a number of platform tags. """


from PyQt4.QtGui import QCheckBox, QDialog

from .Designer.PlatformPickerBase import Ui_PlatformPickerBase


class PlatformPickerDialog(QDialog, Ui_PlatformPickerBase):
    """
    This class implements the dialog for selecting a number of platform tags.
    """
    def __init__(self, prj, code, parent):
        """
        Initialise the dialog.

        prj is the containing project.
        code is the code item.
        parent is the parent widget.
        """
        super(PlatformPickerDialog, self).__init__(parent)

        self.setupUi(self)

        self._plistall = prj.platforms.split()
        plistset = code.platforms.split()

        # Initialise the dialog.
        for p_nr, p in enumerate(self._plistall):
            cb = QCheckBox(p)

            if p in plistset:
                cb.setChecked(True)

            self.layout().insertWidget(p_nr, cb)

    def fields(self):
        """
        Return a tuple of the dialog fields.
        """
        pl = []

        for p_nr in range(self.layout().count()):
            cb = self.layout().itemAt(p_nr).widget()
            if not isinstance(cb, QCheckBox):
                break

            if cb.isChecked():
                pl.append(self._plistall[p_nr])

        return (" ".join(pl), )
